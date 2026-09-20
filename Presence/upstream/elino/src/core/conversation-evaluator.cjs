'use strict';

// ====== 発話タイミング制御エンジン ======
// naturalモード時、STT入力に対して「返す/相槌/黙る」を判断する

const NATURAL_CONFIG = {
  addressThreshold: 0.42,
  thresholds: {
    backchannel: 0.38,
    shortReply: 0.60,
    fullReply: 0.82
  },
  cooldowns: {
    fullReply: 8,
    shortReply: 5,
    backchannel: 2.5
  },
  pressureDecayPerSec: 0.02,
  pressurePerFullReply: 0.4,
  pressurePerShortReply: 0.2,
  pressurePerBackchannel: 0.05,
  observationMinLength: 6,
  maxObservationQueue: 10,
  backchannelHistorySize: 5
};

// 状態
let conversationPressure = 0;
let observationQueue = [];
let lastActionAt = { fullReply: 0, shortReply: 0, backchannel: 0 };
let recentBackchannels = [];

// === メインエントリー ===
function evaluateUtterance(text, ctx) {
  // Phase 1: ADDRESS判定
  const addressScore = calcAddressScore(text, ctx);

  // Phase 2: TURN判定
  const turnState = detectTurnState(ctx);

  // addressScore低い → 黙る（observation候補）
  if (addressScore < NATURAL_CONFIG.addressThreshold) {
    return maybeSilentWithObservation(text, ctx);
  }

  // Phase 3: ACTION選択
  const actionNeed = calcActionNeedScore(text, ctx);
  const combined = addressScore * 0.55 + actionNeed * 0.45;
  const emotionMult = calcEmotionMultiplier(ctx.emotion);
  const pressureAdj = combined * (1 - conversationPressure * 0.3);
  const finalScore = pressureAdj * emotionMult;

  const action = decideActionFromTurnAndScore(text, ctx, { finalScore, turnState });

  // ログ出力
  logEvaluation(text, { addressScore, turnState, actionNeed, finalScore, action });

  // 会話圧更新
  updatePressure(action.type);

  // アクション時刻記録
  if (action.type !== 'SILENT') {
    lastActionAt[action.type === 'FULL_REPLY' ? 'fullReply' :
                  action.type === 'SHORT_REPLY' ? 'shortReply' : 'backchannel'] = Date.now();
  }

  return action;
}

// === ADDRESS判定 ===
function calcAddressScore(text, ctx) {
  let score = 0;
  const hasName = containsName(text, ctx.companionName);
  const isQ = isQuestion(text);
  const hasAddr = hasAddressMarker(text);
  const recentConvo = ctx.lastElinoSpokeAt && secsSince(ctx.lastElinoSpokeAt) < 30;

  if (hasName) score += 0.35;
  if (isQ) score += 0.12;
  if (isQ && hasAddr) score += 0.10;  // 相互作用項
  if (isQ && recentConvo) score += 0.08;  // 相互作用項
  if (recentConvo) score += 0.20;
  if (hasAddr) score += 0.15;

  // 減点
  if (text.length < 3) score -= 0.20;
  if (isFillerOnly(text)) score -= 0.40;

  return clamp(score, 0, 1);
}

// === TURN判定 ===
function detectTurnState(ctx) {
  if (ctx.isUserSpeaking) return 'IN_TURN';
  const silenceMs = ctx.lastUserVoiceEndedAt
    ? Date.now() - ctx.lastUserVoiceEndedAt
    : 2000;
  if (silenceMs < 500) return 'IN_TURN';
  if (silenceMs < 1200) return 'POSSIBLE_BOUNDARY';
  return 'END_OF_TURN';
}

// === ACTION選択（TURN × スコア） ===
function decideActionFromTurnAndScore(text, ctx, { finalScore, turnState }) {
  const t = NATURAL_CONFIG.thresholds;

  if (turnState === 'IN_TURN') {
    if (finalScore >= 0.45 && canBackchannel()) {
      return { type: 'BACKCHANNEL', text: selectBackchannel(ctx) };
    }
    return maybeSilentWithObservation(text, ctx);
  }

  if (turnState === 'POSSIBLE_BOUNDARY') {
    if (finalScore >= t.shortReply && canShortReply()) {
      return { type: 'SHORT_REPLY' };
    }
    if (finalScore >= t.backchannel && canBackchannel()) {
      return { type: 'BACKCHANNEL', text: selectBackchannel(ctx) };
    }
    return maybeSilentWithObservation(text, ctx);
  }

  // END_OF_TURN
  if (finalScore >= t.fullReply && canFullReply()) return { type: 'FULL_REPLY' };
  if (finalScore >= t.shortReply && canShortReply()) return { type: 'SHORT_REPLY' };
  if (finalScore >= t.backchannel && canBackchannel()) {
    return { type: 'BACKCHANNEL', text: selectBackchannel(ctx) };
  }
  return maybeSilentWithObservation(text, ctx);
}

// === 感情6軸 → 微調整係数 ===
function calcEmotionMultiplier(emotion) {
  if (!emotion) return 1.0;
  let mult = 1.0;
  mult *= lerp(0.90, 1.15, emotion.curiosity || 0.5);
  mult *= lerp(0.95, 1.10, emotion.trust || 0.5);
  mult *= lerp(0.75, 1.00, 1 - (emotion.fatigue || 0));
  return mult;
}

// === ActionNeedスコア ===
function calcActionNeedScore(text, ctx) {
  let score = 0.3; // ベース
  // 感情が強い発話
  if (hasStrongEmotion(text)) score += 0.25;
  // 具体的な話題がある
  if (text.length > 15) score += 0.10;
  // まだELINOが拾ってない話題がqueueにある
  if (observationQueue.length > 0) score += 0.05;
  // 相談・困り事っぽい
  if (looksLikeTrouble(text)) score += 0.20;
  return clamp(score, 0, 1);
}

// === 相槌選択（感情ベース + 連発防止） ===
function selectBackchannel(ctx) {
  const e = ctx.emotion || {};
  const v = e.valence || 0;
  const a = e.arousal || 0.5;
  const c = e.curiosity || 0.5;

  let candidates;
  if (v > 0.3 && a > 0.6) {
    candidates = ['いいじゃん', 'おー！', 'それいいね', 'すご'];
  } else if (v < -0.2) {
    candidates = ['そっか…', 'それしんどいね', 'まじか…', 'それは大変だ'];
  } else if (c > 0.7) {
    candidates = ['へえ、それ気になる', 'なるほど', 'もっと聞きたいかも', 'ほう'];
  } else if (a < 0.3) {
    candidates = ['うん', 'へえ', 'なるほど', 'たしかに'];
  } else {
    candidates = ['なるほど', 'たしかに', 'うんうん', 'へー', 'そうなんだ'];
  }

  // 直近使った相槌を除外
  const filtered = candidates.filter(c => !recentBackchannels.includes(c));
  const pick = filtered.length > 0 ? filtered : candidates;
  const selected = pick[Math.floor(Math.random() * pick.length)];

  // 履歴更新
  recentBackchannels.push(selected);
  if (recentBackchannels.length > NATURAL_CONFIG.backchannelHistorySize) {
    recentBackchannels.shift();
  }

  return selected;
}

// === 会話圧 ===
function updatePressure(actionType) {
  const add = {
    FULL_REPLY: NATURAL_CONFIG.pressurePerFullReply,
    SHORT_REPLY: NATURAL_CONFIG.pressurePerShortReply,
    BACKCHANNEL: NATURAL_CONFIG.pressurePerBackchannel,
    SILENT: 0
  }[actionType] || 0;
  conversationPressure = clamp(conversationPressure + add, 0, 1);
}

function decayPressure(userUtteranceChars) {
  conversationPressure = Math.max(0, conversationPressure - NATURAL_CONFIG.pressureDecayPerSec);
  // ユーザーが長く話したら追加減衰
  if (userUtteranceChars && userUtteranceChars > 20) {
    conversationPressure = Math.max(0, conversationPressure - 0.08);
  }
}

// === Observation Queue ===
function maybeSilentWithObservation(text, ctx) {
  if (shouldEnqueueObservation(text, ctx)) {
    enqueueObservation(text, ctx);
  }
  return { type: 'SILENT' };
}

function shouldEnqueueObservation(text, ctx) {
  if (!text || text.trim().length < NATURAL_CONFIG.observationMinLength) return false;
  if (isFillerOnly(text)) return false;
  if (isNearDuplicate(text, observationQueue)) return false;
  return true;
}

function enqueueObservation(text, ctx) {
  observationQueue.push({
    text: text.trim(),
    createdAt: Date.now(),
    emotion: ctx.emotion ? { valence: ctx.emotion.valence, arousal: ctx.emotion.arousal } : null
  });
  if (observationQueue.length > NATURAL_CONFIG.maxObservationQueue) {
    observationQueue.shift();
  }
}

function getAndClearObservations() {
  const items = [...observationQueue];
  observationQueue = [];
  return items;
}

// === ヘルパー ===
function containsName(text, name) {
  if (!name) return false;
  return text.toLowerCase().includes(name.toLowerCase());
}

function isQuestion(text) {
  if (text.includes('？') || text.includes('?')) return true;
  // 日本語疑問語
  return /(?:何|なに|なん|どう|どこ|いつ|誰|だれ|なぜ|どれ|どの|どっち|いくつ|いくら|かな|かしら)[？?]?$/.test(text);
}

function hasAddressMarker(text) {
  return /^(?:ねえ|あのさ|ちょっと|なあ|おい|hey|oi)/i.test(text);
}

function isFillerOnly(text) {
  return /^(?:えー?と?|あー?|うー?ん?|んー?|はぁ|ふー?ん?|あのー?)\s*$/.test(text.trim());
}

function hasStrongEmotion(text) {
  return /[！!]{2,}|やばい|最悪|最高|つらい|しんどい|嬉しい|楽しい|無理|ヤバ/.test(text);
}

function looksLikeTrouble(text) {
  return /困|悩|どうし[よたて]|わから[んない]|辛い|助けて|やばい|無理|終わっ/.test(text);
}

function isNearDuplicate(text, queue) {
  const t = text.trim().toLowerCase();
  return queue.some(item => {
    const existing = item.text.toLowerCase();
    return existing === t || (t.length > 8 && existing.includes(t.slice(0, 8)));
  });
}

function clamp(v, min, max) { return Math.min(max, Math.max(min, v)); }
function lerp(a, b, t) { return a + (b - a) * clamp(t, 0, 1); }
function secsSince(ts) { return ts ? (Date.now() - ts) / 1000 : Infinity; }

function canFullReply() {
  return secsSince(lastActionAt.fullReply) >= NATURAL_CONFIG.cooldowns.fullReply;
}
function canShortReply() {
  return secsSince(lastActionAt.shortReply) >= NATURAL_CONFIG.cooldowns.shortReply;
}
function canBackchannel() {
  return secsSince(lastActionAt.backchannel) >= NATURAL_CONFIG.cooldowns.backchannel;
}

// === ログ ===
function logEvaluation(text, info) {
  const short = text.length > 30 ? text.slice(0, 30) + '...' : text;
  console.log(`[EVAL] "${short}" addr=${info.addressScore.toFixed(2)} turn=${info.turnState} need=${info.actionNeed.toFixed(2)} final=${info.finalScore.toFixed(2)} → ${info.action.type}${info.action.text ? ` "${info.action.text}"` : ''}`);
}

module.exports = {
  evaluateUtterance,
  decayPressure,
  getAndClearObservations,
  NATURAL_CONFIG,
  // テスト用
  _internal: { calcAddressScore, detectTurnState, selectBackchannel, observationQueue: () => observationQueue }
};
