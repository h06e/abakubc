from abaqus import *
from abaqusConstants import *

def make_job(mdb, job_name, test, scratch):
    mdb.Job(name=job_name, model='Model-1', description='', type=ANALYSIS,
            atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=10,
            memoryUnits=GIGA_BYTES, getMemoryFromAnalysis=True,
            explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
            modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
            scratch=scratch, resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1,
            numGPUs=0)