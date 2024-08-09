import torch
import torch.nn as nn
import torch.utils.data
from torch import Tensor
from typing import Iterator


def char_maps(text: str):
    """
    Create mapping from the unique chars in a text to integers and
    vice-versa.
    :param text: Some text.
    :return: Two maps.
        - char_to_idx, a mapping from a character to a unique
        integer from zero to the number of unique chars in the text.
        - idx_to_char, a mapping from an index to the character
        represented by it. The reverse of the above map.

    """
    # TODO:
    #  Create two maps as described in the docstring above.
    #  It's best if you also sort the chars before assigning indices, so that
    #  they're in lexical order.
    # ====== YOUR CODE: ======
    sorted_chars = sorted(set(text))
    char_to_idx = {}
    idx_to_char = {}
    for index, char in enumerate(sorted_chars):
        char_to_idx[char] = index
        idx_to_char[index] = char
    # ========================
    return char_to_idx, idx_to_char


def remove_chars(text: str, chars_to_remove):
    """
    Removes all occurrences of the given chars from a text sequence.
    :param text: The text sequence.
    :param chars_to_remove: A list of characters that should be removed.
    :return:
        - text_clean: the text after removing the chars.
        - n_removed: Number of chars removed.
    """
    # TODO: Implement according to the docstring.
    # ====== YOUR CODE: ======
    black_list_chars_set = set(chars_to_remove)
    text_clean=''.join([char for char in text if char not in black_list_chars_set])

    n_removed = len(text) - len(text_clean)
    # ========================
    return text_clean, n_removed


def chars_to_onehot(text: str, char_to_idx: dict) -> Tensor:
    """
    Embed a sequence of chars as a tensor containing the one-hot encoding
    of each char. A one-hot encoding means that each char is represented as
    a tensor of zeros with a single '1' element at the index in the tensor
    corresponding to the index of that char.
    :param text: The text to embed.
    :param char_to_idx: Mapping from each char in the sequence to it's
    unique index.
    :return: Tensor of shape (N, D) where N is the length of the sequence
    and D is the number of unique chars in the sequence. The dtype of the
    returned tensor will be torch.int8.
    """
    # TODO: Implement the embedding.
    # ====== YOUR CODE: ======
    indices = [char_to_idx[c] for c in text if c in char_to_idx]
    N = len(indices)
    D = len(char_to_idx)
    result = torch.zeros((N,D), dtype=torch.int8)
    result[torch.arange(N),indices]=1
    # ========================
    return result


def onehot_to_chars(embedded_text: Tensor, idx_to_char: dict) -> str:
    """
    Reverses the embedding of a text sequence, producing back the original
    sequence as a string.
    :param embedded_text: Text sequence represented as a tensor of shape
    (N, D) where each row is the one-hot encoding of a character.
    :param idx_to_char: Mapping from indices to characters.
    :return: A string containing the text sequence represented by the
    embedding.
    """
    # TODO: Implement the reverse-embedding.
    # ====== YOUR CODE: ======
    _,indices = torch.max(embedded_text, dim=1, keepdim=False)
    result = ''.join(idx_to_char[i.item()] for i in indices if i.item() in idx_to_char)
    # ========================
    return result


def chars_to_labelled_samples(text: str, char_to_idx: dict, seq_len: int, device="cpu"):
    """
    Splits a char sequence into smaller sequences of labelled samples.
    A sample here is a sequence of seq_len embedded chars.
    Each sample has a corresponding label, which is also a sequence of
    seq_len chars represented as indices. The label is constructed such that
    the label of each char is the next char in the original sequence.
    :param text: The char sequence to split.
    :param char_to_idx: The mapping to create and embedding with.
    :param seq_len: The sequence length of each sample and label.
    :param device: The device on which to create the result tensors.
    :return: A tuple containing two tensors:
    samples, of shape (N, S, V) and labels of shape (N, S) where N is
    the number of created samples, S is the seq_len and V is the embedding
    dimension.
    """
    # TODO:
    #  Implement the labelled samples creation.
    #  1. Embed the given text.
    #  2. Create the samples tensor by splitting to groups of seq_len.
    #     Notice that the last char has no label, so don't use it.
    #  3. Create the labels tensor in a similar way and convert to indices.
    #  Note that no explicit loops are required to implement this function.
    # ====== YOUR CODE: ======
    # Number of full samples we can extract
    # Number of full samples we can extract
    N = (len(text) - 1) // seq_len
    S = seq_len
    V = len(char_to_idx)

    # Trim the text to fit full samples
    trimmed_text = text[:N * S + 1]  # include one extra for labels

    # Embed the trimmed text except the last character
    embedded_text = chars_to_onehot(trimmed_text[:-1],
                                    char_to_idx)  # we got a matrix where each row is one character embedded in dim V
    # We want to group every s rows to an array
    samples = embedded_text.view((N, S, V)).to(device)
    # Prepare labels: indices of the next characters in the sequence
    shifted_indices_str = [char_to_idx[c] for c in trimmed_text[1:] if c in char_to_idx]
    labels = torch.tensor(shifted_indices_str).view((N, S)).to(device)
    # ========================
    return samples, labels



def hot_softmax(y, dim=0, temperature=1.0):
    """
    A softmax which first scales the input by 1/temperature and
    then computes softmax along the given dimension.
    :param y: Input tensor.
    :param dim: Dimension to apply softmax on.
    :param temperature: Temperature.
    :return: Softmax computed with the temperature parameter.
    """
    # TODO: Implement based on the above.
    # ====== YOUR CODE: ======
    scaled = y/temperature if temperature !=0 else temperature
    result = torch.softmax(scaled, dim=dim)
    # ========================
    return result


def generate_from_model(model, start_sequence, n_chars, char_maps, T):
    """
    Generates a sequence of chars based on a given model and a start sequence.
    :param model: An RNN model. forward should accept (x,h0) and return (y,
    h_s) where x is an embedded input sequence, h0 is an initial hidden state,
    y is an embedded output sequence and h_s is the final hidden state.
    :param start_sequence: The initial sequence to feed the model.
    :param n_chars: The total number of chars to generate (including the
    initial sequence).
    :param char_maps: A tuple as returned by char_maps(text).
    :param T: Temperature for sampling with softmax-based distribution.
    :return: A string starting with the start_sequence and continuing for
    with chars predicted by the model, with a total length of n_chars.
    """
    assert len(start_sequence) < n_chars
    device = next(model.parameters()).device
    char_to_idx, idx_to_char = char_maps
    out_text = start_sequence
    # TODO:
    #  Implement char-by-char text generation.
    #  1. Feed the start_sequence into the model.
    #  2. Sample a new char from the output distribution of the last output
    #     char. Convert output to probabilities first.
    #     See torch.multinomial() for the sampling part.
    #  3. Feed the new char into the model.
    #  4. Rinse and Repeat.
    #  Note that tracking tensor operations for gradient calculation is not
    #  necessary for this. Best to disable tracking for speed.
    #  See torch.no_grad().
    # ====== YOUR CODE: ======
    #embedded_x0 = chars_to_onehot(start_sequence, char_to_idx) #(N,D) where N is sequence length and D is embedded dim
    #embedded_x0 = embedded_x0.view(1, len(start_sequence),-1) #(1,N,D) 1 batch, N sequence length and D is embedded dim for input
    #y, h = model(embedded_x0.to(dtype=torch.float, device=device)) # y (1,N,D) 1 batch, N sequence length and O is embedded dim for output. h is (1,L,H). 1 for batch, 3 for 3 layers and H is dimension of memory
    #output_for_word_generation = y[:,-1,:]
    #first_char_generation_distribution= hot_softmax(output_for_word_generation,dim=-1,temperature=T) #each row in the output has column for each possible char
    #first_char_idx = torch.multinomial(first_char_generation_distribution, num_samples=1)
    #out_text+=idx_to_char[first_char_idx.item()]

    str_input=start_sequence
    hidden_state=None
    with torch.no_grad():
        for i in range(n_chars-len(start_sequence)):
            embedded_input = chars_to_onehot(str_input, char_to_idx)
            embedded_input = embedded_input.unsqueeze(0)
            y, h = model(embedded_input.to(dtype=torch.float, device=device), hidden_state)
            output_for_word_generation = y[:, -1, :]
            distribution =  hot_softmax(output_for_word_generation,dim=-1,temperature=T)
            char_idx = torch.multinomial(distribution, num_samples=1)
            generated_char = idx_to_char[char_idx.item()]
            out_text+=generated_char

            str_input= generated_char
            hidden_state = h
    # ========================

    return out_text


class SequenceBatchSampler(torch.utils.data.Sampler):
    """
    Samples indices from a dataset containing consecutive sequences.
    This sample ensures that samples in the same index of adjacent
    batches are also adjacent in the dataset.
    """

    def __init__(self, dataset: torch.utils.data.Dataset, batch_size):
        """
        :param dataset: The dataset for which to create indices.
        :param batch_size: Number of indices in each batch.
        """
        super().__init__(dataset)
        self.dataset = dataset
        self.batch_size = batch_size

    def __iter__(self) -> Iterator[int]:
        # TODO:
        #  Return an iterator of indices, i.e. numbers in range(len(dataset)).
        #  dataset and represents one  batch.
        #  The indices must be generated in a way that ensures
        #  that when a batch of size self.batch_size of indices is taken, samples in
        #  the same index of adjacent batches are also adjacent in the dataset.
        #  In the case when the last batch can't have batch_size samples,
        #  you can drop it.
        idx = None  # idx should be a 1-d list of indices.
        # ====== YOUR CODE: ======
        num_batches = len(self.dataset) // self.batch_size
        data_set_size = num_batches*self.batch_size
        array = torch.arange(0, data_set_size)
        batches_as_matrix = array.view(-1, num_batches).t()
        idx = batches_as_matrix.reshape(data_set_size).tolist()

        # ========================
        return iter(idx)

    def __len__(self):
        return len(self.dataset)


class MultilayerGRU(nn.Module):
    """
    Represents a multi-layer GRU (gated recurrent unit) model.
    """

    def __init__(self, in_dim, h_dim, out_dim, n_layers, dropout=0):
        """
        :param in_dim: Number of input dimensions (at each timestep).
        :param h_dim: Number of hidden state dimensions.
        :param out_dim: Number of input dimensions (at each timestep).
        :param n_layers: Number of layer in the model.
        :param dropout: Level of dropout to apply between layers. Zero
        disables.
        """
        super().__init__()
        assert in_dim > 0 and h_dim > 0 and out_dim > 0 and n_layers > 0

        self.in_dim = in_dim
        self.out_dim = out_dim
        self.h_dim = h_dim
        self.n_layers = n_layers
        self.layer_params = []

        # TODO: READ THIS SECTION!!

        # ====== YOUR CODE: ======
        for i in range(n_layers):
           curr_layer_params = {}

           input_dim = self.in_dim if i == 0 else self.h_dim
           curr_layer_params["wxz"] = nn.Linear(input_dim, h_dim, bias=False)
           curr_layer_params["whz"] =  nn.Linear(h_dim, h_dim, bias=True)
           curr_layer_params["wxr"] = nn.Linear(input_dim, h_dim, bias=False)
           curr_layer_params["whr"] = nn.Linear(h_dim, h_dim, bias=True)
           curr_layer_params["wxg"] = nn.Linear(input_dim, h_dim, bias=False)
           curr_layer_params["whg"] = nn.Linear(h_dim, h_dim, bias=True)

           self.layer_params.append(curr_layer_params)

           for param_name, layer in curr_layer_params.items():
               self.add_module(f"{i}_{param_name}", layer)

        self.dropout = nn.Dropout(p=dropout)
        self.why = nn.Linear(h_dim, self.out_dim, bias=True)
        # ========================


    def forward(self, input: Tensor, hidden_state: Tensor = None):
        """
        :param input: Batch of sequences. Shape should be (B, S, I) where B is
        the batch size, S is the length of each sequence and I is the
        input dimension (number of chars in the case of a char RNN).
        :param hidden_state: Initial hidden state per layer (for the first
        char). Shape should be (B, L, H) where B is the batch size, L is the
        number of layers, and H is the number of hidden dimensions.
        :return: A tuple of (layer_output, hidden_state).
        The layer_output tensor is the output of the last RNN layer,
        of shape (B, S, O) where B,S are as above and O is the output
        dimension.
        The hidden_state tensor is the final hidden state, per layer, of shape
        (B, L, H) as above.
        """
        batch_size, seq_len, _ = input.shape

        layer_states = [] #if we look at the picture we can see each layer get as input: h_t(k) which is related to the input element entered in time k
        #it also uses memory ht-1(k) i.e a memory of that specific layer
        for i in range(self.n_layers):
            if hidden_state is None: # if no initial hidden states are gives, just init with zeros
                layer_states.append(
                    torch.zeros(batch_size, self.h_dim, device=input.device)
                )
            else:
                layer_states.append(hidden_state[:, i, :]) #hidden states has size (B,L,H). this line will take for us row i on the entire cube which
                #is ok because it will take the hidden state for the entire batch. we insert (B,H) to the array

        layer_input = input
        layer_output = None

        # TODO: READ THIS SECTION!!
        # ====== YOUR CODE: ======
        # Loop over layers of the model
        for layer_idx in range(self.n_layers): #we are looping on layers! so each iteration we are processing entire sequence for layer i
            wxz = self.layer_params[layer_idx]["wxz"]  #update gate
            whz = self.layer_params[layer_idx]["whz"] #update gate
            wxr = self.layer_params[layer_idx]["wxr"] #reset gate
            whr = self.layer_params[layer_idx]["whr"] #reset gate
            wxg = self.layer_params[layer_idx]["wxg"] #candidate hidden state
            whg = self.layer_params[layer_idx]["whg"] #candidate hidden state

            h_t = layer_states[layer_idx]  # (B, H)
            layer_outputs = []

            # Loop over items in the sequence
            for seq_idx in range(seq_len):
                x_t = layer_input[:, seq_idx, :]  # (B, V) or (B, H)

                z_t = torch.sigmoid(wxz(x_t) + whz(h_t)) #role-percentage how much to save from original memory versus new candidate memory
                r_t = torch.sigmoid(wxr(x_t) + whr(h_t)) #role-percentage how much to save from the original memory in the new candidate memory
                g_t = torch.tanh(wxg(x_t) + whg(r_t * h_t))
                h_t = z_t * h_t + (1 - z_t) * g_t

                layer_outputs.append(h_t)  # (B, H)

            # Save last state as layer state
            layer_states[layer_idx] = h_t

            # Combine the output from each element in the sequence to a tensor
            # representing the output of the entire sequence
            layer_output = torch.stack(layer_outputs, dim=1)  # (B, S, H)

            # Prepare input for next layer
            layer_input = self.dropout(layer_output)  # (B, S, H)

        # Final output: transform the input to the next (non-existent) layer
        layer_output = self.why(layer_input)  # (B, S, O)
        hidden_state = torch.stack(layer_states, dim=1)  # (B, L, H)
        # ========================
        return layer_output, hidden_state
