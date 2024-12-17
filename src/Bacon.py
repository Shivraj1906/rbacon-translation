import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import fitz # to convert pdf to image
import pickle # dump the object to a file
from rpy2.robjects import r, conversion, default_converter
from rpy2.robjects.packages import importr

class Bacon:
    def __init__(self, file_path, core_name, cc=1, acc_mean=20, acc_shape=1.5, mem_strength=10, mem_mean=0.5, load = False) -> None:
        if load:
            # load the object from the pickle file
            fp = open(f'./Bacon_runs/{core_name}/{core_name}.pkl', 'rb')
            obj = pickle.load(fp)
            fp.close()
            # copy the attributes from the loaded object
            self.__dict__ = obj.__dict__
            # we have to reinitialize the R environment
            params = f'\'{self.core_name}\', suggest=FALSE, accept.suggestions=TRUE, acc.mean={self.acc_mean}, acc.shape={self.acc_shape}, mem.strength={self.mem_strength}, mem.mean={self.mem_mean}'
            with conversion.localconverter(default_converter):
                # suppress the output to the console
                grdevices = importr('grDevices')
                grdevices.pdf(file="/dev/null")
                # load the Bacon package and run the Bacon function
                r('install.packages("rbacon")')            
                importr('rbacon')
                r(f'Bacon({params}, run=FALSE)')
                r(f'agedepth()')
                r('dev.off()')
            return
        self.file_path = file_path
        self.core_name = core_name
        self.acc_mean = acc_mean
        self.acc_shape = acc_shape
        self.mem_strength = mem_strength
        self.mem_mean = mem_mean

        # read the csv file
        self.data = pd.read_csv(file_path) # assume that this is the input csv file

        # preprocessing of the data to add optional columns
        self.data['cc'] = cc

        # create a folder with the labid name
        os.makedirs(f'./Bacon_runs/{self.core_name}', exist_ok=True)
        self.data.to_csv(f'./Bacon_runs/{self.core_name}/{self.core_name}.csv', index=False)

        # run the model
        self.run()

    def run(self):
        with conversion.localconverter(default_converter):
            # suppress the output to the console
            grdevices = importr('grDevices')
            grdevices.pdf(file="/dev/null")
            # prepare the parameters
            params = f'\'{self.core_name}\', suggest=FALSE, accept.suggestions=TRUE, acc.mean={self.acc_mean}, acc.shape={self.acc_shape}, mem.strength={self.mem_strength}, mem.mean={self.mem_mean}'

            # import the Bacon package and run the Bacon function
            r('install.packages("rbacon")') 
            importr('rbacon')
            r(f'Bacon({params})')

            # read the 'info' variable from R environment
            self.info = r('info')

    def inspect_run(self):
        pdf_path = f'./Bacon_runs/{self.core_name}/{self.core_name}_21.pdf'
        doc = fitz.open(pdf_path)
        page = doc[0]
        pix = page.get_pixmap(dpi=300)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        
        # Display the image using matplotlib
        fig, ax = plt.subplots()
        ax.imshow(img)
        ax.axis('off')  # Hide the axis
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1)  # Adjust the subplot to remove margins
        plt.show()

    def predict_age(self, depth):
        with conversion.localconverter(default_converter):
            r(f'a.{depth} <- Bacon.Age.d({depth})')
            data = r(f'a.{depth}')

        # data is of type 'rpy2.robjects.vectors.FloatVector' convert it to numpy array
        data = np.array(data)

        # print the mean of data
        print(f'\nMean of the data at depth {depth} is {data.mean()} Cal years BP')

        # plot the data in a histogram
        plt.hist(data, bins=20)
        plt.xlabel('Age')
        plt.ylabel('Frequency')
        plt.title(f'Mean of the data at depth {depth} is {data.mean():.1f} Cal years BP')
        plt.show()

    def predict_timespan(self, depth1, depth2):
        with conversion.localconverter(default_converter):
            r(f'a1.{depth1} <- Bacon.Age.d({depth1})')
            r(f'a2.{depth2} <- Bacon.Age.d({depth2})')
            r(f't.{depth1}_{depth2} <- a1.{depth1} - a2.{depth2}')
            data = r(f't.{depth1}_{depth2}')

        data = np.array(data)

        print(f'\nMean of the data between depths {depth1} and {depth2} is {data.mean()} Cal years BP')

        #plot the data in a histogram
        plt.hist(data, bins=20)
        plt.xlabel('Age')
        plt.ylabel('Frequency')
        plt.title(f'Mean of the data between depths {depth1} and {depth2} is {data.mean():.1f} Cal years BP')
        plt.show()

    def predict_acc_rate(self, depth):
        with conversion.localconverter(default_converter):
            r(f'acc.{depth} <- accrate.depth({depth})')
            data = r(f'acc.{depth}')

        data = np.array(data)

        print(f'\nMean of the data at depth {depth} is {data.mean()} yr/cm')

        #plot the data in a histogram
        plt.hist(data, bins=20)
        plt.xlabel('Accumulation Rate')
        plt.ylabel('Frequency')
        plt.title(f'Mean of the data at depth {depth} is {data.mean():.1f} yr/cm')
        plt.show()

    def dump(self):
        # dump the object to a pickle file
        fp = open(f'./Bacon_runs/{self.core_name}/{self.core_name}.pkl', 'wb')
        pickle.dump(self, fp)
        fp.close()