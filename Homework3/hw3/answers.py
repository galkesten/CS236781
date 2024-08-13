r"""
Use this module to write your answers to the questions in the notebook.

Note: Inside the answer strings you can use Markdown format and also LaTeX
math (delimited with $$).
"""

# ==============
# Part 1 answers


def part1_rnn_hyperparams():
    hypers = dict(
        batch_size=0,
        seq_len=0,
        h_dim=0,
        n_layers=0,
        dropout=0,
        learn_rate=0.0,
        lr_sched_factor=0.0,
        lr_sched_patience=0,
    )
    # TODO: Set the hyperparameters to train the model.
    # ====== YOUR CODE: ======
    hypers = dict(
        batch_size=128,
        seq_len=64,
        h_dim=512,
        n_layers=3,
        dropout=0.1,
        learn_rate=0.001,
        lr_sched_factor=0.1,
        lr_sched_patience=3,
    )
    # ========================
    return hypers


def part1_generation_params():
    start_seq = ""
    temperature = 0.0001
    # TODO: Tweak the parameters to generate a literary masterpiece.
    # ====== YOUR CODE: ======
    start_seq = "Act I."

    temperature = 0.3
    # ========================
    return start_seq, temperature


part1_q1 = r"""
We split the corpus due to the following reasons:

1)**Preventing Vanishing and Exploding Gradients:** 
During the training of RNNs, backpropagation through time (BPTT) is used to update weights. 
If the sequences are too long, the gradients can either vanish or explode, leading to training difficulties 
and numeric instability. Splitting the text into shorter sequences helps mitigate this issue by limiting the
number of time steps over which gradients need to be propagated, thus stabilizing the training process.

2)**Memory Limits:** Since RNNs process each token sequentially, we need to keep the hidden state for each time step until we perform backpropagation. If the sequences are too long, the memory consumption can become excessive, potentially exceeding available resources. Splitting the corpus into shorter sequences helps manage memory usage more efficiently.

3 )**Batch Processing:** Even though RNNs process tokens sequentially within each sample, 
dividing the corpus into smaller sequences allows us to process tokens from different samples in
parallel within a batch. This parallel processing enhances computational efficiency, making the training process
faster.

4)**Focusing on Local Context:** For many language tasks, the local context (nearby words or tokens) is
most relevant for making predictions. Splitting the text into sequences allows the RNN to focus on learning from
these local contexts, making it easier to model short-term dependencies that are crucial for tasks like sequence
prediction.



"""

part1_q2 = r"""
During training, the model processes sequences of a limited length,
grouped into batches. Each sample in a batch continues in the next batch,
meaning that sample I in batch j continues as sample I in batch j+1. This setup ensures that the model's
hidden state, which captures the learned context, is transferred from one batch to the next. 
As a result, the model retains memory across batches, allowing it to understand a longer context than
the sequence length might suggest. Even though the optimization happens within the scope of each sequence,
the continuity provided by the hidden state transfer means the model learns from a broader context. 
During inference, this allows the model to generate meaningful longer sequences.
The batch size used during training influences how context is preserved across sequences.
A larger batch size tends to break the corpus into smaller, more isolated segments, as each position
in the batch retains its individual memory and context. In contrast, a smaller batch size allows the model to
carry context over longer sections of text,
as it processes more batches and maintains continuity across them.

"""

part1_q3 = r"""
We are not shuffling the order of batches because each sample in a batch continues
into the next batch. Ensuring that batches follow one another in the correct order allows the model
to transfer the hidden state from one batch to the next, preserving the learned context across batches.
This continuity enables the model to understand longer sequences than the individual sequence length might suggest.
Shuffling the batches would disrupt this continuity, preventing the model from effectively learning the relationships
between consecutive elements and undermining its ability
to retain and utilize long-term dependencies.

"""

part1_q4 = r"""
1.Lowering the temperature modifies the softmax function to create a sharper probability distribution.
This means that the probabilities diverge more significantly, with higher probabilities becoming even higher,
and lower probabilities becoming closer to zero. Lowering the temperature is used to make the model outputs 
more predictable and less random by emphasizing more probable outcomes. When T=1, , as observed from the plot above,
many characters share similar distributions, so the output may become too random and lack coherence
(since each character is sampled based on the distribution).


2.When the temperature is set very high, the effect on the softmax function is to make the output probability
distribution more uniform. This happens because a high temperature effectively diminishes
the differences between the logits that are input to the softmax function.
The model becomes less able to distinguish between more likely and less likely outcomes. 
This can lead to less coherent or meaningful outputs, as the model does not strongly
prefer more probable predictions based on the training data.

3.When the temperature is very low the softmax distribution becomes very "peaky,"
with the probability mass concentrated on one or very few logits that have the highest values.
As a result, the model's output becomes more deterministic, with the most likely
outcomes chosen frequently. This can lead to more predictable and reliable output, 
but it may also cause the output to repeat itself often.
"""
# ==============


# ==============
# Part 2 answers

PART2_CUSTOM_DATA_URL = None


def part2_vae_hyperparams():
    hypers = dict(
        batch_size=0, h_dim=0, z_dim=0, x_sigma2=0, learn_rate=0.0, betas=(0.0, 0.0),
    )
    # TODO: Tweak the hyperparameters to generate a former president.
    # ====== YOUR CODE: ======
    hypers["batch_size"] = 96
    hypers["h_dim"] = 512
    hypers["z_dim"] = 64
    hypers["x_sigma2"] = 0.1
    hypers["learn_rate"] = 0.0002
    hypers["betas"] = (0.5, 0.999)
    # ========================
    return hypers


def part3_gan_hyperparams():
    hypers = dict(
        batch_size=0, z_dim=0, discriminator_optimizer=dict(type="", lr=0.0, betas=(0.0, 0.0)),
        generator_optimizer=dict(type="", lr=0.0, betas=(0.0, 0.0)), data_label=0,label_noise=0.0
    )
    # TODO: Tweak the hyperparameters to generate a former president.
    # ====== YOUR CODE: ======
    hypers["batch_size"] =8
    hypers["z_dim"] = 100
    hypers["discriminator_optimizer"] = {
        "type": "Adam",
        "lr": 0.0002,
        "betas": (0.5, 0.999),
    }

    hypers["generator_optimizer"] = {
        "type": "Adam",
        "lr": 0.0002,
        "betas": (0.5, 0.999),
    }

    hypers["data_label"] = 0
    hypers["label_noise"] = 0.4
    # ========================
    return hypers

part2_q1 = r"""
In GANs, we train two networks simultaneously—the generator and the discriminator.
We use an alternating optimization method, where in one step,
we optimize the discriminator while keeping the generator fixed. In the next step,
we fix the discriminator and optimize the generator. These networks are trained with different loss functions.

When training the discriminator, we focus on teaching it to differentiate between real data and fake data,
assuming the generator is fixed. To do this, we must sample fake data from the generator to train the discriminator.
However, since the generator's parameters are not being updated in this step (as it's fixed during this step),
we do not need to maintain the gradients. The purpose of gradients is to optimize the weights in the generator network,
and we don't optimize the generator during the discriminator optimization step.

On the other hand, when training the generator, our goal is to improve its
ability to fool the discriminator with the samples it creates. Since the generator aims to improve,
we do maintain the gradients so that we can optimize the data generation process and make it better over time.

"""

part2_q2 = r"""
1. No, we should not stop GAN training solely based on the generator loss being below a certain threshold. 
GAN training should ideally be stopped when both the generator and discriminator reach a point of Nash equilibrium,
where neither network can improve significantly without the other also improving, indicating a balance in their
adversarial game. Our goal is not simply to see the generator loss decrease,
as is common in other machine learning settings. If the generator loss consistently decreases during training,
it might suggest that the discriminator is too weak, allowing the generator to fool it with samples that aren't
necessarily realistic. Therefore, it's important to also monitor the discriminator loss, ensuring it isn't too high
(indicating a weak model) or too low (indicating a very strong model that could prevent the generator from
learning effectively).What we're aiming for is to find that Nash equilibrium point, which is generally challenging to identify.
Instead of just focusing on loss reduction, better indicators for stopping training include monitoring the losses of 
both models and checking when they aren't improving significantly, reflecting the zero-sum nature of GANs. 
Another indicator is the value of the discriminator loss. At the optimal point of Nash equilibrium, 
the discriminator should have difficulty differentiating between real and fake data,
resulting in a classification probability of around 0.5 for both. 
This would correspond to a cross-entropy loss for the discriminator close to 0.6. 



"""

part2_q3 = r"""
**Your answer:**



"""

part2_q4 = r"""
**Your answer:**


"""

# ==============

# ==============
# Part 3 answers

PART3_CUSTOM_DATA_URL = None


def part3_transformer_encoder_hyperparams():
    hypers = dict(
        embed_dim = 0, 
        num_heads = 0,
        num_layers = 0,
        hidden_dim = 0,
        window_size = 0,
        droupout = 0.0,
        lr=0.0,
    )

    # TODO: Tweak the hyperparameters to train the transformer encoder.
    # ====== YOUR CODE: ======
    
    # ========================
    return hypers




part3_q1 = r"""
**Your answer:**

"""

part3_q2 = r"""
**Your answer:**


"""


part4_q1 = r"""
**Your answer:**


"""

part4_q2 = r"""
**Your answer:**


"""


part4_q3= r"""
**Your answer:**


"""

part4_q4 = r"""
**Your answer:**


"""

part4_q5 = r"""
**Your answer:**


"""


# ==============
