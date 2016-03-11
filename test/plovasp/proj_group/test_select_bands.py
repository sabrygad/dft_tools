
import os
import rpath
_rpath = os.path.dirname(rpath.__file__) + '/'

import numpy as np
import pytriqs.applications.dft.converters.plovasp.vaspio as vaspio
import pytriqs.applications.dft.converters.plovasp.elstruct as elstruct
from pytriqs.applications.dft.converters.plovasp.inpconf import ConfigParameters
from pytriqs.applications.dft.converters.plovasp.proj_shell import ProjectorShell
from pytriqs.applications.dft.converters.plovasp.proj_group import ProjectorGroup
import mytest

################################################################################
#
# TestSelectBands
#
################################################################################
class TestSelectBands(mytest.MyTestCase):
    """
    Function:

    def ProjectorGroup.select_bands(eigvals)

    Scenarios:
    - compare output for a correct input
    - **if** emin > max(eigvals) **raise** Exception
    - **if** emax > min(eigvals) **raise** Exception
    """
    def setUp(self):
        conf_file = _rpath + 'simple.cfg'
        self.pars = ConfigParameters(conf_file)
        self.pars.parse_input()
        vasp_data = vaspio.VaspData(_rpath + 'simple/')
        self.el_struct = elstruct.ElectronicStructure(vasp_data)

        efermi = vasp_data.doscar.efermi
        self.eigvals = vasp_data.eigenval.eigs - efermi

        self.proj_sh = ProjectorShell(self.pars.shells[0], vasp_data.plocar.plo, vasp_data.plocar.proj_params, 0)
        self.proj_gr = ProjectorGroup(self.pars.groups[0], [self.proj_sh], self.eigvals)

# Scenario 1
    def test_correct(self):
        ib_win, nb_min, nb_max = self.proj_gr.select_bands(self.eigvals)

        nb_min_exp = 3
        nb_max_exp = 8
        ib_win_exp = np.array([[[3, 8]], [[3, 7]], [[3, 7]], [[3, 7]], [[3, 7]], [[3, 7]], [[3, 7]], [[3, 4]]])

        self.assertEqual(nb_min, nb_min_exp)
        self.assertEqual(nb_max, nb_max_exp)
        self.assertEqual(ib_win, ib_win_exp)

# Scenario 2
    def test_emin_too_large(self):
        self.proj_gr.emin = 20.0
        self.proj_gr.emax = 25.0
        with self.assertRaisesRegexp(Exception, "No bands inside the window"):
            ib_win, nb_min, nb_max = self.proj_gr.select_bands(self.eigvals)

# Scenario 3
    def test_emax_too_small(self):
        self.proj_gr.emin = -50.0
        self.proj_gr.emax = -55.0
        with self.assertRaisesRegexp(Exception, "Energy window does not overlap"):
            ib_win, nb_min, nb_max = self.proj_gr.select_bands(self.eigvals)


