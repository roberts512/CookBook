# -*- coding: UTF-8 -*-
'''
Created on 2012-11-27

@author: tianwei
'''
import os
import sys
from dumbo import cmd, util
from dumbo.util import Options
import numpy
from scipy.linalg import norm

"""Configure"""
MAXIterations = 100
DistanceResult = 1e-3
HADOOP_PATH = os.environ["HADOOP_HOME"]


class KmeansControl(object):
    """
    Kmeans Control Class Logical
    """
    exDir = os.path.abspath(os.path.dirname(__file__))
    exProgram = os.path.join(exDir, "kmeans.py")

    clusterData = "clusters.csv"

    prevNorm = None
    currNorm = None

    def __init__(self, ishadoop=False, filepath=None):
        self.maxs = MAXIterations
        self.rightResult = DistanceResult
        self.ishadoop = ishadoop
        
        if self.ishadoop:
            self.dataDir = filepath
        else:
            self.dataDir =  os.path.join(self.exDir,"data") 
        
        self.resultDir = os.path.join(self.dataDir,'result')
        self.sourceData = os.path.join(self.dataDir,"data.csv")

        self.patialSource = os.path.join(self.dataDir,self.clusterData)
        self.patialResult = None

    def calculateResult(self,previous_result = None, current_result = None):
        """
        """
        if not current_result:
            return False
        
        #import file to numpy array
        prevArray = numpy.loadtxt(previous_result)
        currArray = numpy.loadtxt(current_result)
       
        #TODO: maybe we should use another method
        sumV = 0
        for i in range(0,len(prevArray)):
            sumV += norm(currArray[i]-prevArray[i])

        self.currNorm = sumV

        if self.prevNorm is None:
            self.preNorm = sumV
            ret = False
        else:
            ret = True if abs(self.prevNorm - self.currNorm) < self.rightResult else False
            self.preNorm = sumV
        
        return ret
 
    def setup(self):
        """
        Initial setup code
        """
        
        if self.ishadoop:
            return
        #delete the results file
        for f in os.listdir(self.resultDir):
            name = os.path.join(self.resultDir,f)
            try:
                os.remove(name)
            except:
                pass

    def clean(self):
        """
        clean the resource 
        """
        pass

    def run(self):
        """
        """
        self.setup()
        
        print "Step1 : every iteration"
        
        ###################
        #Calculate Process
        for i in range(0,self.maxs):        
            distResult = self.calculateResult(previous_result=self.patialSource,current_result=self.patialResult) 
            if distResult or i > self.maxs:
                break
            
            self.patialResult = os.path.join(self.resultDir ,self.clusterData+"_"+str(i))

            result = self.jobRun(
                    inputfile = self.sourceData,
                    clusterfile= self.patialSource, 
                    outputfile=self.patialResult
                    )

            if result != 0:
                raise ValueError("%s kmeans iteration ERROR!!"%(i))

            self.patialSource = self.patialResult

        ###############
        #show the graph
        print "End of this kmeans algorightm!"        

        self.clean()

    def jobRun(self,inputfile = None , clusterfile = None, outputfile = None):
        """
        every map-reduce job

        Args:
            inputfile: clusterfile of this stage
            outputfile : patial result , which need to be calculated for
            distance to end kmeans calculate process
        """
       
        args = " dumbo start " + self.exProgram
        if self.ishadoop:
            args += " -hadoop " + HADOOP_PATH
        
        args += " -input " + inputfile
        args += " -output " + outputfile 
        args += " -param clusters_file=" + clusterfile

        print args 

        return os.system(args)

def main(argv):
    """
    main thread
    """
    if len(argv) == 4 and argv[2] == "hadoop":
        k = KmeansControl(ishadoop=True,filename = argv[3])
        k.run()
    else:
        k = KmeansControl()
        k.run()

if __name__ == "__main__":
    main(sys.argv)