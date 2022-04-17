import pytest
import torch

from espnet2.diar.loss.wrappers.pit_solver_2 import PITSolver2
from espnet2.enh.loss.criterions.tf_domain import FrequencyDomainL1


@pytest.mark.parametrize("num_spk", [1, 2, 3])
def test_PITSolver_forward(num_spk):

    batch = 2
    inf = [torch.rand(batch, 10, 100) for spk in range(num_spk)]
    ref = [inf[num_spk - spk - 1] for spk in range(num_spk)]  # reverse inf as ref
    solver = PITSolver2(FrequencyDomainL1(), independent_perm=True)

    loss, stats, others = solver(ref, inf)
    perm = others["perm"]
    correct_perm = list(range(num_spk))
    correct_perm.reverse()
    assert perm[0].equal(torch.tensor(correct_perm))

    # test for independent_perm is False

    solver = PITSolver2(FrequencyDomainL1(), independent_perm=False)
    loss, stats, others = solver(ref, inf, {"perm": perm})
