__author__ = 'quentin'


import unittest
import shutil
import random
import tempfile
import logging
import numpy as np

from ethoscope.rois.roi_builders import ROI
from ethoscope.utils.io import ResultWriter, SQLiteResultWriter
from ethoscope.core.variables import DataPoint, BoolVariableBase, IntVariableBase, DistanceIntVarBase

class DummyBoolVariable(BoolVariableBase):
    header_name="dummy_bool"

class DummyIntVariable(IntVariableBase):
    functional_type = "dum_type"
    header_name="dummy_int"

class DummyDistVariable(DistanceIntVarBase):
    header_name="dummy_dist_int"

class XVar(DistanceIntVarBase):
    header_name="x"

class YVar(DistanceIntVarBase):
    header_name="y"

class RandomResultGenerator(object):
    def make_one_point(self):

        out = DataPoint([
                DummyBoolVariable(bool(int(random.uniform(0,2)))),
                DummyIntVariable(random.uniform(0,1000)),
                DummyDistVariable(random.uniform(0,1000)),
                XVar(random.uniform(0,1000)),
                YVar(random.uniform(0,1000)),
                ])
        return out


class TestMySQL(unittest.TestCase):

    def _test_dbwriter(self, RWClass, *args, **kwargs):
        """
        This test hardcode ROIs and generate random results for a set of arbitrary variables.
        The goal is to be able to test and benchmark result write independently of any tracking

        :return:
        """
        # building five rois
        coordinates = np.array([(0,0), (100,0), (100,100), (0,100)])
        rois = [ROI(coordinates +i*100) for i in range(1,33)]
        rpg = RandomResultGenerator()

        with RWClass(rois=rois, *args, **kwargs) as rw:
            # n = 4000000 # 222h of data
            # n = 400000 # 22.2h of data
            n = 40000 # 2.22h of data
            import time
            t0 = time.time()
            for t in range(0, n):
                rt = t * 1000 /5

                if t % (n/100)== 0:
                    logging.info("filling with dummy variables: %f percent" % (100.*float(t)/float(n)))
                for r in rois:
                    data = rpg.make_one_point()
                    rw.write(rt , r, data)
                print time.time() - t0
                rw.flush(t)



    def test_sqlite(self):
        logging.getLogger().setLevel(logging.INFO)
        a = tempfile.mkdtemp(prefix="psv_results_")

        try:

            self._test_dbwriter(SQLiteResultWriter,a)
            self.assertEqual(1, 1)
        finally:
            logging.info(a)
            shutil.rmtree(a)

    def test_mysql(self):
        logging.getLogger().setLevel(logging.INFO)
        self._test_dbwriter(ResultWriter, db_name="psv_test_io")
