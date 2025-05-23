#!/usr/bin/env python3

import argparse
from pandas import read_csv
from pandas import DataFrame
from pandas import Grouper
from matplotlib import pyplot as plt
import pandas as pd


def main(csv_file, put, runs, cut_off, step, out_file, fuzzers):
  #Read the results
  df = read_csv(csv_file)

  #Calculate the mean of code coverage
  #Store in a list first for efficiency
  mean_list = []

  for subject in [put]:
    for fuzzer in fuzzers:
      for data_type in ['nodes', 'edges']:
        #get subject & fuzzer & cov_type-specific dataframe
        df1 = df[(df['subject'] == subject) & 
                         (df['fuzzer'] == fuzzer) & 
                         (df['state_type'] == data_type)]

        mean_list.append((subject, fuzzer, data_type, 0, 0.0))
        for time in range(1, cut_off + 1, step):
          cov_total = 0
          run_count = 0

          for run in range(1, runs + 1, 1):
            #get run-specific data frame
            df2 = df1[df1['run'] == run]

            try:
              #get the starting time for this run
              start = df2.iloc[0, 0]

              #get all rows given a cutoff time
              df3 = df2[df2['time'] <= start + time*60]
              
              #update total coverage and #runs
              cov_total += df3.tail(1).iloc[0, 5]
              run_count += 1
            except Exception:
              print("Issue with run {}. Skipping".format(run))
          
          #add a new row
          mean_list.append((subject, fuzzer, data_type, time, cov_total / max(run_count,1)))

  #Convert the list to a dataframe
  mean_df = pd.DataFrame(mean_list, columns = ['subject', 'fuzzer', 'data_type', 'time', 'data'])
  
  # save to file
  print("Saving mean logs into file...")
  mean_df.to_csv("mean_plot_data.csv", index=False)

  # Set global font sizes
  plt.rcParams.update({'font.size': 30})

  fig, axes = plt.subplots(1, 2, figsize = (40, 20))
  fig.suptitle("State coverage analysis", fontsize=20)

  ylim = 0
  lines = []
  for key, grp in mean_df.groupby(['fuzzer', 'data_type']):
    if key[1] == 'nodes':
      line = axes[0].plot(grp['time'], grp['data'])
      lines.extend(line)
      axes[0].set_xlabel('Time (in min)')
      axes[0].set_ylabel('#nodes')
    if key[1] == 'edges':
      line = axes[1].plot(grp['time'], grp['data'])
      axes[1].set_xlabel('Time (in min)')
      axes[1].set_ylabel('#edges')
      if max(grp['data']) > ylim:
        axes[1].set_ylim([0, max(grp['data'])+20])
        ylim = max(grp['data']) + 20

  for ax in fig.axes:
    ax.grid()

  fig.legend(lines[:len(fuzzers)], fuzzers, loc='center left', bbox_to_anchor=(1.0, 0.5))
  
  plt.tight_layout()

  #Save to file
  plt.savefig(out_file, bbox_inches='tight')

# Parse the input arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()    
    parser.add_argument('-i','--csv_file',type=str,required=True,help="Full path to plot_data.csv")
    parser.add_argument('-p','--put',type=str,required=True,help="Name of the subject program")
    parser.add_argument('-r','--runs',type=int,required=True,help="Number of runs in the experiment")
    parser.add_argument('-c','--cut_off',type=int,required=True,help="Cut-off time in minutes")
    parser.add_argument('-s','--step',type=int,required=True,help="Time step in minutes")
    parser.add_argument('-o','--out_file',type=str,required=True,help="Output file")
    parser.add_argument('-f','--fuzzers', nargs='+',required=True,help="List of fuzzers")
    args = parser.parse_args()
    main(args.csv_file, args.put, args.runs, args.cut_off, args.step, args.out_file, args.fuzzers)