from googleapiclient.discovery import build

class DriveHunter:
    def __init__(self, creds_file, token_file):
        self.service = build("drive", "v3", credentials=self._load_creds(creds_file, token_file))

    def _load_creds(self, creds_file, token_file):
        # TODO: implement proper OAuth loading
        pass

    def hunt_files(self, keywords):
        results = []
        for kw in keywords:
            query = f"name contains '{kw}'"
            files = self.service.files().list(q=query).execute()
            for f in files.get("files", []):
                results.append(f"Drive hit: {kw} in {f['name']}")
        return results
