"

def compute_gei(silhouette_frames):
    stack = np.stack(silhouette_frames, axis=0).astype(np.float32)
    return np.mean(stack, axis=0)


class GaitIdentifier:
    def __init__(self, db_path="data/gait/", similarity_threshold=0.75):
        self.db_path = db_path
        self.similarity_threshold = similarity_threshold
        self.known_geis = {}
        self._load_known_geis()

    def _load_known_geis(self):
        if not os.path.isdir(self.db_path):
            return
        for fname in os.listdir(self.db_path):
            if fname.endswith(".npy"):
                self.known_geis[fname[:-4]] = np.load(os.path.join(self.db_path, fname))

    def register_gait(self, name, silhouette_frames):
        gei = compute_gei(silhouette_frames)
        os.makedirs(self.db_path, exist_ok=True)
        np.save(os.path.join(self.db_path, f"{name}.npy"), gei)
        self.known_geis[name] = gei

    def identify(self, silhouette_frames):
        if len(silhouette_frames) < 5:
            return None
        query_gei = compute_gei(silhouette_frames)
        best_name, best_score = None, -1.0
        for name, gei in self.known_geis.items():
            score = _cosine_similarity(query_gei.flatten(), gei.flatten())
            if score > best_score:
                best_name, best_score = name, score
        return best_name if best_score >= self.similarity_threshold else None


def _cosine_similarity(a, b):
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8
    return float(np.dot(a, b) / denom)
