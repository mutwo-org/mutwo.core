# This file is part of mutwo, ecosystem for time-based arts.
#
# Copyright (C) 2020-2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import sys
import unittest


__all__ = ("ModuleImportTest",)


class ModuleImportTest(unittest.TestCase):
    """Test that any order of import subpackages works.

    In namespace packages we do not explicitly declare the import order
    of submodules. Therefore some circular import problems can appear
    in case the user picks a wrong import order. Any mutwo package should
    prevent these errors. This tests checks that any import order of
    modules work without any problem.
    """

    module_name_list = []

    def _test_import(self, module_name: str):
        try:
            exit_code = subprocess.run(
                [sys.executable, "-c", f"from mutwo import {module_name}"],
                check=True,
            ).returncode
        except subprocess.CalledProcessError as e:
            failure_information = f"Import of 'mutwo.{module_name}' failed: {e}"
            exit_code = 1
        else:
            failure_information = ""

        self.assertEqual(0, exit_code, failure_information)

    def test_module_import(self):
        for module_name in self.module_name_list:
            with self.subTest(module_name=module_name):
                self._test_import(module_name)
