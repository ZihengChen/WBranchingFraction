import utility_common as common
from pylab import *
from utility_bfsolver import *
from tqdm import tqdm, trange

class BFSovler3D_Error:
    def __init__(self):
        self.tb = BFSolver_Toolbox()
        self.baseDir = common.getBaseDirectory() 

        counts = pd.read_pickle( self.baseDir + "data/counts/count_.pkl")
        
        self.a, self.aVar = counts.acc, counts.accVar
        self.ndata, self.ndataVar = counts.ndata, counts.ndataVar
        self.nmcbg, self.nmcbgVar = counts.nmcbg, counts.nmcbgVar
        self.nfake, self.nfakeVar = counts.nfake, counts.nfakeVar
        
    
    def errStat(self, errSource):
    
        errs = []
        for icata in range(4):
            a,aVar  = self.a[icata], self.aVar[icata]
            ndata,ndataVar = self.ndata[icata],self.ndataVar[icata]
            nmcbg,nmcbgVar = self.nmcbg[icata],self.nmcbgVar[icata]
            nfake,nfakeVar = self.nfake[icata],self.nfakeVar[icata]

            slv = BFSolver3D(a)
            BW  = slv.solveQuadEqn(slv.setMeasuredX(nData=ndata, nMcbg=nmcbg+nfake))

            ## data: by err propagation
            if errSource == "data":

                dBW = []
                for c in range(4):
                    # variate ndata to ndata1
                    ndata1 = ndata.copy()
                    ndata1[c] = ndata[c] + ndataVar[c]**0.5
                    # get BW1 corresponding to ndata1
                    BW1 = slv.solveQuadEqn(slv.setMeasuredX(nData=ndata1, nMcbg=nmcbg+nfake))
                    # push deriveratives
                    dBW.append( BW1-BW )
                dBW = np.array(dBW)
                # propagating error
                errFromSource = np.sum(dBW**2,axis=0)**0.5
            
            ## mcbg: by std of toys which variate mcbg
            elif errSource == "mcbg":
            
                dBW = []
                for c in range(4):
                    # variate nmcbg to nmcbg1
                    nmcbg1 = nmcbg.copy()
                    nmcbg1[c] = nmcbg[c]+nmcbgVar[c]**0.5
                    # get BW1 corresponding to nmcbg1
                    BW1 = slv.solveQuadEqn(slv.setMeasuredX(nData=ndata, nMcbg=nmcbg1+nfake))
                    # push deriveratives
                    dBW.append( BW1-BW )
                dBW = np.array(dBW)
                # propagating error
                errFromSource = np.sum(dBW**2,axis=0)**0.5

            ## mcbg: by std of toys which variate mcbg
            elif errSource == "fake":
                dBW = []
                for c in range(4):
                    # variate nfake to nfake1
                    nfake1 = nfake.copy()
                    nfake1[c] = nfake[c]+nfakeVar[c]**0.5
                    # get BW1 corresponding to nfake1
                    BW1 = slv.solveQuadEqn(slv.setMeasuredX(nData=ndata, nMcbg=nmcbg+nfake1))
                    # push deriveratives
                    dBW.append( BW1-BW )
                dBW = np.array(dBW)
                # propagating error
                errFromSource = np.sum(dBW**2,axis=0)**0.5

            elif errSource == "mcsg":
                dBW = []
                for c in range(4):
                    for i in range(6):
                        for j in range(6):
                            # variate a to a1
                            if i == j and a[c,i,j]>0.001: 
                                # variate a to a1
                                a1 = a.copy()
                                a1[c,i,j] = a[c,i,j] + aVar[c,i,j]**0.5
                                # get BW1 corresponding to a1
                                slv1 = BFSolver3D(a1)
                                BW1  = slv1.solveQuadEqn(slv1.setMeasuredX(nData=ndata, nMcbg=nmcbg+nfake))
                                dBW.append( BW1-BW )
                
                            if i < j :#and a[c,i,j]>0.001:
                                # variate a to a1
                                a1 = a.copy()
                                a1[c,i,j] = a[c,i,j] + aVar[c,i,j]**0.5
                                a1[c,j,i] = a[c,j,i] + aVar[c,j,i]**0.5
                                # get BW1 corresponding to a1
                                slv1 = BFSolver3D(a1)
                                BW1 = slv1.solveQuadEqn(slv1.setMeasuredX(nData=ndata, nMcbg=nmcbg+nfake))
                                dBW.append( BW1-BW )
                dBW = np.array(dBW)
                # propagating error
                errFromSource = np.sum(dBW**2,axis=0)**0.5

            else:
                print("invalid stat err source")
                
            errs.append(errFromSource)

        errs = np.array(errs)
        return errs
    
    def errSystem_crossSection(self, errSource):
        errs = []
        for icata in range(4):

            a     = self.a[icata]
            ndata = self.ndata[icata]
            nmcbg = self.nmcbg[icata]
            nfake = self.nfake[icata]

            slv = BFSolver3D(a)
            if errSource == "mcbg":
                BW  = slv.solveQuadEqn(slv.setMeasuredX(nData=ndata, nMcbg=nmcbg+nfake))
                BW1 = slv.solveQuadEqn(slv.setMeasuredX(nData=ndata, nMcbg=1.05*nmcbg+nfake))
            elif errSource == "fake":
                BW  = slv.solveQuadEqn(slv.setMeasuredX(nData=ndata, nMcbg=nmcbg+nfake))
                BW1 = slv.solveQuadEqn(slv.setMeasuredX(nData=ndata, nMcbg=nmcbg+nfake*1.15))
            elif errSource == "mcsg":
                BW  = slv.solveQuadEqn(slv.setMeasuredX(nData=ndata, nMcbg=nmcbg+nfake))
                slv1 = BFSolver3D(1.05*a)
                BW1 = slv1.solveQuadEqn(slv1.setMeasuredX(nData=ndata, nMcbg=nmcbg+nfake))
            else:
                print("invalid stat err source")
            errs.append(BW1-BW)                
        errs = np.array(errs)
        return errs

    def errSystem_objectEff(self,errSource):
        errs = []
        for icata in range(4):

            a     = self.a[icata]
            ndata = self.ndata[icata]
            nmcbg = self.nmcbg[icata]
            nfake = self.nfake[icata]

            slv = BFSolver3D(a)
                
            if errSource == "e":
                effUp = np.array([0.01,0,0,0]) + 1
            elif errSource == "mu":
                effUp = np.array([0,0.01,0,0]) + 1
            elif errSource == "tau":
                effUp = np.array([0,0,0.05,0]) + 1
            else:
                print("invalid stat err source")

            BW = slv.solveQuadEqn(slv.setMeasuredX(nData=ndata, nMcbg=nmcbg+nfake))
            ## tuning up a
            slv1 = BFSolver3D( effUp[:,None,None]*a )
            ## tuning up nmcbg
            BW1  = slv1.solveQuadEqn(slv1.setMeasuredX(nData=ndata, nMcbg=effUp*nmcbg+nfake))
            errs.append(BW1-BW)                
        
        errs = np.array(errs)
        return errs


    def errSystem_energyScale(self,errSource="e"):
        errs = []

        counts1 = pd.read_pickle(self.baseDir + "data/counts/count_{}.pkl".format(errSource+"PtDown"))

        for icata in range(4):
            
            # nominal tuning
            slv  = BFSolver3D(self.a[icata])
            BW   = slv.solveQuadEqn(slv.setMeasuredX(nData=self.ndata[icata], nMcbg=self.nmcbg[icata]+self.nfake[icata]))
            # down tuning
            slv1 = BFSolver3D( counts1.acc[icata] )
            BW1  = slv1.solveQuadEqn(slv1.setMeasuredX(nData=counts1.ndata[icata], nMcbg=counts1.nmcbg[icata]+counts1.nfake[icata]))
            # difference between down and nominal
            errs.append(BW1-BW) 

        errs = np.array(errs)
        return errs


    def errSystem_upDownVariation(self,errSource="JES"):
        '''
        "ISR","FSR","UE","MEPS","JES","JER","BTag","Mistag","Renorm","Factor","PDF"
        '''


        counts1 = pd.read_pickle(self.baseDir + "data/counts/count_{}.pkl".format(errSource+"Up"))
        counts2 = pd.read_pickle(self.baseDir + "data/counts/count_{}.pkl".format(errSource+"Down"))


        errs = []
        for icata in range(4):
                
            # up tuning
            slv1 = BFSolver3D( counts1.acc[icata] )
            BW1  = slv1.solveQuadEqn(slv1.setMeasuredX(nData=counts1.ndata[icata], nMcbg=counts1.nmcbg[icata]+counts1.nfake[icata]))
            # down tuning
            slv2 = BFSolver3D( counts2.acc[icata] )
            BW2  = slv2.solveQuadEqn(slv2.setMeasuredX(nData=counts2.ndata[icata], nMcbg=counts2.nmcbg[icata]+counts2.nfake[icata]))
            # differentce between up and down tuning
            errs.append((BW1-BW2)/2)
                
        errs = np.array(errs)
        return errs


    def io_printErrorForExcelFormat(self,error):
        error = np.abs(error/0.1086 * 100)

        for i in range(error.shape[1]):
            print("{:5.3f},{:5.3f},{:5.3f}, {:5.3f},{:5.3f},{:5.3f}, {:5.3f},{:5.3f},{:5.3f}, {:5.3f},{:5.3f},{:5.3f}" \
                .format(error[0,i,0],error[0,i,1],error[0,i,2],
                        error[1,i,0],error[1,i,1],error[1,i,2],
                        error[2,i,0],error[2,i,1],error[2,i,2],
                        error[3,i,0],error[3,i,1],error[3,i,2]
                    ))

    def smearAcc(self,a,aVar):
        smear = np.zeros_like(a)
        # loop over channels
        for slt in range(4): 
            # loop over hight
            for i in range(smear.shape[0]):
                # loop over width
                for j in range(smear.shape[1]):
                    # action on half element and above thrd = 0.001
                    if (i<=j) & (a[slt,i,j]>0.001):
                        smear[slt,i,j] = np.random.normal( 0, aVar[slt,i,j]**0.5)
                        if i != j :
                            smear[slt,j,i] = smear[slt,i,j]
        return smear
