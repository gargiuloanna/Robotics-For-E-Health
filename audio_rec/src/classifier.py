import numpy as np

import torch

from WavLM import WavLM, WavLMConfig

class Classifier:

    SR = 16000

    def __init__(self, data_path, model_path, threshold=0.85) -> None:
        self.data_path = data_path
        self.threshold = threshold
        self.emb_dim = 1024 if "Large" in model_path else 768
        self.model_path = model_path
        self._load_model()
        self._load_support()

    def __len__(self):
        return self.support_set.shape[0]
    
    def pcm2float(self, sig, dtype='float32'):
        """Convert PCM signal to floating point with a range from -1 to 1.
        Use dtype='float32' for single precision.
        Parameters
        ----------
        sig : array_like
            Input array, must have integral type.
        dtype : data type, optional
            Desired (floating point) data type.
        Returns
        -------
        numpy.ndarray
            Normalized floating point data.
        See Also
        --------
        float2pcm, dtype
        """
        return sig.astype(np.float32, order='C') / 32768.0

    def _load_model(self):
        # Load the pytorch model
        checkpoint = torch.load(self.model_path)
        cfg = WavLMConfig(checkpoint['cfg'])
        self.model = WavLM(cfg)
        self.model.load_state_dict(checkpoint['model'])
        self.model.eval()

    def _get_representation(self, audio):
        # Extract embeddings
        audio = torch.Tensor([audio])
        rep = self.model.extract_features(audio)[0].detach().numpy()
        x = np.mean(rep[0], axis=0)

        # Compute the norm
        return x/np.linalg.norm(x)

    def batch_cosine_similarity(self, x1, x2):
        # Compute cosine similarity assuming normalized vectors
        mul = np.multiply(x1, x2)
        s = np.sum(mul, axis=1)

        return s

    def _update_support(self, audio, y):
        audio = self.pcm2float(audio)
        # Add new sample to the support set
        rep = self._get_representation(audio)
        self.support_set = np.append(
            self.support_set, np.expand_dims(rep, 0), axis=0)

        self.y.append(y)

    def _load_support(self):
        # modules needed only for this function
        import os
        import librosa

        files_path = []
        self.y = []

        # get list of paths
        for root, _, files in os.walk(self.data_path, topdown=False):
            for name in files:
                # add path to file
                files_path.append(os.path.join(root, name))
                # add class of the file
                self.y.append(os.path.basename(root))

        self.support_set = np.zeros((len(files_path), self.emb_dim))
        # Load files and get embedding
        for i in range(len(files_path)):
            audio, _ = librosa.load(files_path[i], sr=16000)
            self.support_set[i] = self._get_representation(audio)

    def predict(self, audio):
        audio = self.pcm2float(audio)

        # Get embedding from audio
        x = self._get_representation(audio)

        # Replicate to parallelize comparison
        emb_voice = np.vstack([x for _ in range(self.support_set.shape[0])])

        # Cosine distance
        cos_dist = self.batch_cosine_similarity(self.support_set, emb_voice)

        # Matching
        return self.dist2id(cos_dist, self.y, mode='avg')

    def dist2id(self, distance, y, mode='avg'):
        # Set delle identità
        ids = list(set(y))
        y = np.array(y)

        # Aggregazione similarità per identità
        ids_prob = []
        for i in ids:
            if mode == 'max':
                ids_prob.append(np.max(distance[y == i]))
            if mode == 'avg':
                ids_prob.append(np.mean(distance[y == i]))
            if mode == 'min':
                ids_prob.append(np.min(distance[y == i]))

        ids_prob = np.array(ids_prob)

        # Ricerca del massimo
        max_idx = np.argmax(ids_prob)
        prob = ids_prob[max_idx]

        # Rigetto
        identity = ids[max_idx] if prob >= self.threshold else None

        return identity, prob, ids[max_idx]


if __name__ == "__main__":
    clf = Classifier('sounds')
