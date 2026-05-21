import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def main():
    df = pd.read_csv("results.csv", sep=';')
    # get the values of NUM_SERVERS, t_decrypt.
    x = df["NUM_SERVERS"]
    y = df["t_decrypt"]
    plt.plot(x, y, label="t_decrypt", marker='o', linestyle='')
    plt.xlabel("Number of Servers")
    plt.ylabel("Time (seconds)")
    plt.title("Time taken to decrypt ballots vs number of servers")
    plt.legend()
    
    #print the linear regression line for the data
    m, b = np.polyfit(x, y, 1)


    plt.show()



if __name__ == "__main__":
    main()