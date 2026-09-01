"""Sync selected read-only Gmail, Drive, and OneDrive context into the BPFCoBrain vault."""

import argparse
from pathlib import Path

from drive_hunt import DriveHunter
from gmail_hunt import GmailHunter
from ondrive_hunt import OneDriveHunter
from obsidian_writer import ObsidianWriter


def run_brain(vault_path, credentials_file, token_file, onedrive_token_file, keywords):
    gmail = GmailHunter(credentials_file, token_file)
    drive = DriveHunter(credentials_file, token_file)
    ondrive = OneDriveHunter(onedrive_token_file)
    evidence = []

    # Sync Gmail
    for message in gmail.hunt_keywords(keywords).values():
        item = gmail.read_message(message["id"])
        evidence.append(
            "## Gmail: {subject}\n\n"
            "- **Message ID:** `{id}`\n- **From:** {sender}\n- **Date:** {date}\n\n{body}".format(
                subject=item["subject"] or "(no subject)", id=item["id"], sender=item["from"],
                date=item["date"], body=item["body"] or "(no plain-text body available)"
            )
        )

    # Sync Google Drive
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

    # Sync OneDrive
    try:
        for file_id, file_info in ondrive.hunt_files(keywords).items():
            content = ondrive.read_text(file_id, file_info.get("mimeType"))
            evidence.append(
                "## OneDrive: {name}\n\n"
                "- **File ID:** `{id}`\n- **Modified:** {modified}\n- **Link:** {link}\n\n{content}".format(
                    name=file_info.get("name", "(unnamed)"), id=file_id,
                    modified=file_info.get("modifiedTime", ""), 
                    link=file_info.get("webViewLink", ""),
                    content=content
                )
            )
    except Exception as e:
        print(f"⚠️  OneDrive sync skipped: {e}")

    writer = ObsidianWriter(str(vault_path))
    writer.append_to_evidence(evidence)
    print(f"✅ Synced {len(evidence)} Gmail/Drive/OneDrive records into {vault_path / 'Evidence.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync read-only Gmail, Drive, and OneDrive context into the brain")
    parser.add_argument("keywords", nargs="+", help="Gmail terms, Drive filename terms, and OneDrive search terms")
    parser.add_argument("--vault", default=str(Path(__file__).resolve().parent))
    parser.add_argument("--credentials", default=str(Path(__file__).resolve().parent / "credentials.json"))
    parser.add_argument("--token", default=str(Path(__file__).resolve().parent / "token.json"))
    parser.add_argument("--onedrive-token", default=str(Path(__file__).resolve().parent / "onedrive_token.json"))
    args = parser.parse_args()
    run_brain(Path(args.vault), args.credentials, args.token, args.onedrive_token, args.keywords)
