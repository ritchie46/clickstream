from clickstream.seq2seq import decoder_loss, decoder_loss_batched
import logging

logger = logging.getLogger(__name__)


def run_epoch(
    epoch,
    model,
    optim,
    dataset,
    batch_size,
    teach_forcing_p=0.5,
    device="cpu",
    nullify_rnn_input=False,
    batched=True,
    verbosity=0,
    reverse_target=False,
):
    """
    Train one epoch.

    Parameters
    ----------
    epoch : int
    model : torch.nn.Module
    optim : torch.Optimizer
    dataset : clickstream.data.utils.Dataset
    batch_size : int
    teach_forcing_p : float
    device : str
        "cpu" or "cuda"
    nullify_rnn_input : bool
    batched : bool
    verbosity : int
        0 -> INFO
        1 -> DEBUG
    reverse_target : bool
        Predict the inverted sentence. Leads to cleaner representations.
    """
    model.train()
    n_total = len(dataset)
    dataset.shuffle()

    for i in range(n_total // batch_size):
        optim.zero_grad()
        i = i * batch_size

        packed_padded, padded = dataset.get_batch(i, i + batch_size, device=device)
        if not batched:
            if not nullify_rnn_input:
                logger.warning("Argmument `nullify_rnn_input` is not used when using non batched learning.")
            logger.warning("Argument `teacher_forcing_p` is not used when using non batched learning.")
            loss = decoder_loss(model, padded)
        else:
            loss = decoder_loss_batched(
                model, packed_padded, teach_forcing_p, nullify_rnn_input, reverse_target
            )
        loss.backward()
        optim.step()

    level = logging.DEBUG if verbosity == 0 else logging.INFO
    logger.log(level, "Epoch: {}\tLoss{:.4f}".format(epoch, loss.item()))
