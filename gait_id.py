


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
