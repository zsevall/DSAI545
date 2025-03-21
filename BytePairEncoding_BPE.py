from collections import defaultdict
import re

class BytePairEncoder:
    def __init__(self, vocab_size=100):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.inverse_vocab = {}
        self.merges = {}
    
    def train(self, word_counts):
        # Initialize with characters
        word_freqs = defaultdict(int)
        
        # Preprocess and count word frequencies
        for word, count in word_counts.items():
            word_freqs[' '.join(list(word)) + ' </w>'] += count
        
        # Initialize vocabulary with individual characters
        chars = set()
        for word in word_freqs.keys():
            for char in word.split():
                chars.add(char)
        
        # Add individual characters to vocabulary
        i = 0
        for char in sorted(chars):
            self.vocab[char] = i
            self.inverse_vocab[i] = char
            i += 1
        
        vocab_size = len(self.vocab)
        print(f"Initial vocabulary ({vocab_size} tokens):", self.vocab)
        
        # Merge pairs until we reach the desired vocabulary size
        iterations = 0
        max_iterations = 100  # Safety limit
        
        while vocab_size < self.vocab_size and iterations < max_iterations:
            iterations += 1
            
            # Find the most frequent pair
            pairs = self._get_pairs(word_freqs)
            if not pairs:
                print("No more pairs to merge.")
                break
                
            # Get the pair with highest frequency
            best_pair = max(pairs.items(), key=lambda x: x[1])[0]
            pair_freq = pairs[best_pair]
            
            if pair_freq < 1:
                print("No more frequent pairs.")
                break
                
            print(f"\nMost frequent pair: {best_pair} (frequency: {pair_freq})")
            
            # Create new token for this pair
            new_token = ''.join(best_pair)
            self.merges[best_pair] = new_token
            self.vocab[new_token] = vocab_size
            self.inverse_vocab[vocab_size] = new_token
            vocab_size += 1
            
            # Update word frequencies with the new merged pair
            new_word_freqs = defaultdict(int)
            for word, freq in word_freqs.items():
                new_word = self._merge_word(word, best_pair)
                new_word_freqs[new_word] += freq
            
            # Print the updated words after this merge
            print("Words after merge:")
            for word, freq in sorted(new_word_freqs.items(), key=lambda x: x[1], reverse=True):
                print(f"  {word} (frequency: {freq})")
            
            word_freqs = new_word_freqs
            
            print(f"Vocabulary size: {vocab_size}")
            
            if vocab_size >= self.vocab_size:
                break
        
        if iterations >= max_iterations:
            print("Warning: Reached maximum number of iterations.")
                
    def _get_pairs(self, word_freqs):
        pairs = defaultdict(int)
        for word, freq in word_freqs.items():
            symbols = word.split()
            if len(symbols) < 2:
                continue  # Skip words with only one symbol
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i + 1])] += freq
        return pairs
    
    def _merge_word(self, word, pair):
        first, second = pair
        parts = word.split()
        
        if len(parts) < 2:
            return word  # Can't merge if there's only one token
            
        i = 0
        while i < len(parts) - 1:
            if parts[i] == first and parts[i + 1] == second:
                parts[i:i+2] = [''.join(pair)]
            else:
                i += 1
        return ' '.join(parts)
    
    def print_token_analysis(self, word_counts):
        print("\n--- Token Analysis ---")
        for word, count in word_counts.items():
            print(f"\nWord: '{word}' (frequency: {count})")
            # Start with characters
            tokenized_word = ' '.join(list(word)) + ' </w>'
            print(f"Initial: {tokenized_word}")
            
            # Apply merges in order
            for pair, merged in self.merges.items():
                old_word = tokenized_word
                tokenized_word = self._merge_word(tokenized_word, pair)
                if old_word != tokenized_word:
                    print(f"After merging {pair} → {merged}: {tokenized_word}")
            
            # Final tokens
            print(f"Final tokens: {tokenized_word.split()}")
    
    def encode(self, text):
        tokens = []
        for word in text.split():
            word = ' '.join(list(word)) + ' </w>'
            while True:
                pairs = self._get_pairs({word: 1})
                if not pairs:
                    break
                    
                # Find the highest-ranking pair
                bigram = None
                for pair in pairs.keys():
                    if pair in self.merges:
                        bigram = pair
                        break
                
                # If no pair can be merged, stop
                if bigram is None:
                    break
                    
                # Merge the identified pair
                word = self._merge_word(word, bigram)
            
            # Add the final tokens
            word_tokens = word.split()
            tokens.extend(word_tokens)
        
        # Convert tokens to ids
        token_ids = [self.vocab.get(token, self.vocab.get('</w>')) for token in tokens]
        return token_ids
    
    def decode(self, token_ids):
        # Convert ids back to tokens
        tokens = [self.inverse_vocab.get(id, '</w>') for id in token_ids]
        
        # Merge tokens to reconstruct text
        text = ''.join(tokens).replace('</w>', ' ')
        return text.strip()

# Test the implementation
if __name__ == "__main__":
    # Create corpus with specified frequencies
    word_counts = {
        "low": 5,
        "lowest": 2,
        "newer": 6,
        "under": 3,
        "new": 2
    }

    # Set a reasonable vocab size to see several merges
    bpe = BytePairEncoder(vocab_size=20)
    
    try:
        bpe.train(word_counts)
        
        # Analyze each word's tokenization
        bpe.print_token_analysis(word_counts)
        
        # Print final merges and vocabulary
        print("\n--- Final Merges ---")
        for pair, merged in bpe.merges.items():
            print(f"{pair} → {merged}")
        
        print("\n--- Final Vocabulary ---")
        for token, idx in sorted(bpe.vocab.items(), key=lambda x: x[1]):
            print(f"{idx}: {token}")
            
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()