"""Sync selected read-only Gmail and Drive context into the BPFCoBrain vault."""

import argparse
from pathlib import Path

from drive_hunt import DriveHunter
from gmail_hunt import GmailHunter
from obsidian_writer import ObsidianWriter


def run_brain(vault_path, credentials_file, token_file, keywords):
    gmail = GmailHunter(credentials_file, token_file)
    drive = DriveHunter(credentials_file, token_file)
    evidence = []

    for message in gmail.hunt_keywords(keywords).values():
        item = gmail.read_message(message["id"])
        evidence.append(
            "## Gmail: {subject}\n\n"
            "- **Message ID:** `{id}`\n- **From:** {sender}\n- **Date:** {date}\n\n{body}".format(
                subject=item["subject"] or "(no subject)", id=item["id"], sender=item["from"],
                date=item["date"], body=item["body"] or "(no plain-text body available)"
            )
        )

    for file in drive.hunt_files(keywords).values():
        mime_type = file.get("mimeType", "")
        if mime_type.startswith("application/vnd.google-apps") and mime_type != "application/vnd.google-apps.document":
            continue
        content = drive.read_text(file["id"], mime_type)
        evidence.append(
            "## Drive: {name}\n\n"
            "- **File ID:** `{id}`\n- **Modified:** {modified}\n- **Link:** {link}\n\n{content}".format(
                name=file.get("name", "(unnamed)"), id=file["id"],
                modified=file.get("modifiedTime", ""), link=file.get("webViewLink", ""), content=content
            )
        )

    writer = ObsidianWriter(str(vault_path))
    writer.append_to_evidence(evidence)
    print(f"Synced {len(evidence)} Gmail/Drive records into {vault_path / 'Evidence.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync read-only Gmail and Drive context into the brain")
    parser.add_argument("keywords", nargs="+", help="Gmail terms and Drive filename terms")
    parser.add_argument("--vault", default=str(Path(__file__).resolve().parent))
    parser.add_argument("--credentials", default=str(Path(__file__).resolve().parent / "credentials.json"))
    parser.add_argument("--token", default=str(Path(__file__).resolve().parent / "token.json"))
    args = parser.parse_args()
    run_brain(Path(args.vault), args.credentials, args.token, args.keywords)
