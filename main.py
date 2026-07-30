from gmail_hunt import GmailHunter
from drive_hunt import DriveHunter
from obsidian_writer import ObsidianWriter

def run_brain():
    # Initialize hunters
    gmail = GmailHunter("credentials.json", "token.json")
    drive = DriveHunter("credentials.json", "token.json")
    obsidian = ObsidianWriter(vault_path="./ObsidianVault")

    # Step 1: Fetch evidence from Gmail
    gmail_results = gmail.hunt_keywords(["Capitec", "Invoice", "BPFCo"])
    
    # Step 2: Fetch evidence from Drive
    drive_results = drive.hunt_files(["Capitec", "Invoice", "BPFCo"])
    
    # Step 3: Merge results
    all_evidence = gmail_results + drive_results
    
    # Step 4: Write into Obsidian
    obsidian.append_to_evidence(all_evidence)

if __name__ == "__main__":
    run_brain()
