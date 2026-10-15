import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns

# File settings, add your file path here
file_path = None
file_path = "/Users/hannaht/Desktop/MAT2007- project/Smoking prevalence and cigarette consumption.csv"
#check the working directory --> might have to adjust it to the folde you saved the data to 
print(os.getcwd())
#in case errors occure this is what i did to fix it, run them in the terminal of vs code #cd ~/Desktop/"MAT2007- project" #pwd #python3 script.py

#Folder to save our output plots and tables into 
output_folder = None
output_folder = "smoking_output"

# renaming the long original columns to shorter names
column_rename = None
column_rename = {"Entity": "country", "Year": "year", 'Daily smoking prevalence - male (IHME, GHDx (2012))': "male", 'Daily smoking prevalence - female (IHME, GHDx (2012))': "female",}

#creating a graph outline using seaborn --> makes the graphs prettier by having a consisten layout and adding tick lines for easier interpretation
sns.set_theme(style="ticks",rc={"xtick.minor.visible": True,"ytick.minor.visible": True,})

def load_data():
    raw_smoking_data = None
    new_smoking_data = None

    raw_smoking_data = pd.read_csv(file_path) #read dataset as csv
    new_smoking_data = raw_smoking_data.copy() #make a copy  before changing anything
    return new_smoking_data

def clean_data(new_smoking_data):
    # Rename and select the columns needed
    new_smoking_data = new_smoking_data.rename(columns=column_rename)
    new_smoking_data = new_smoking_data[["country","year","male", "female"] ]

    # Remove the "World" row it is not part of the 187 countries
    new_smoking_data = new_smoking_data[new_smoking_data["country"] != "World"]
    return new_smoking_data

def inspect_data(new_smoking_data):
    # Show some basic information about the data
    print("First five rows:")
    print(new_smoking_data.head()) # first 5 entries
    print("\nNumber of countries:")
    print(new_smoking_data["country"].nunique()) #takes the unique country namesand counts them
    print("\nYears:")
    print(new_smoking_data["year"].min(), "to", new_smoking_data["year"].max()) #gives the year range of the data set

###### Absolute calculations #######
def calculate_yearly_averages(new_smoking_data):
    # Calculate the average prevalence over all countries for each year 
    #grouping the data by year, calculating mean and standard deviations
    yearly = new_smoking_data.groupby("year").agg(
        female_mean=("female", "mean"), male_mean=("male", "mean"),
        female_sd=("female", "std"), male_sd=("male", "std"),
        female_n=("female", "count"), male_n=("male", "count"),
    ).reset_index()
    #the calculations for standard error 
    yearly["female_se"] = yearly["female_sd"] / np.sqrt(yearly["female_n"])
    yearly["male_se"] = yearly["male_sd"] / np.sqrt(yearly["male_n"])
    return yearly

####### Relative Calculation ######
def calculate_relative_decline(yearly):
    # Use the first year in the data as each sex's own baseline
    female_baseline = None
    male_baseline = None
    relative = None
    #use the first year --> 1980 as each sexes baeline
    female_baseline = yearly["female_mean"].iloc[0]
    male_baseline = yearly["male_mean"].iloc[0]
    relative = yearly.copy()
    # % change from baseline, each year, for each sex
    relative["female_relative"] = ((relative["female_mean"] - female_baseline) / female_baseline * 100)
    relative["male_relative"] = ((relative["male_mean"] - male_baseline) / male_baseline * 100)
    return relative

def calculate_relative_slopes(new_smoking_data):
    # Calculate the relative smoking trend for each country better than absolute, now they are actually comparable
    relative_slopes = []
    female_slope = None
    male_slope = None
    country_data = None
    female_baseline = None
    male_baseline = None
    female_relative = None
    male_relative = None

    for country in new_smoking_data["country"].unique():
        country_data = new_smoking_data[new_smoking_data["country"] == country]
        #each countries first year --> 1980 is the baseline for each sex
        female_baseline = country_data["female"].iloc[0]
        male_baseline = country_data["male"].iloc[0]
        # percental change from baseline
        female_relative = (country_data["female"] - female_baseline) / female_baseline * 100
        male_relative = (country_data["male"] - male_baseline) / male_baseline * 100
        #linear regressionssaa``
        female_slope = stats.linregress(country_data["year"], female_relative).slope
        male_slope = stats.linregress(country_data["year"], male_relative).slope
        
        relative_slopes.append({"country": country, "female_slope": female_slope, "male_slope": male_slope})
    return pd.DataFrame(relative_slopes)

######## Statistical Test #########
def run_paired_t_test(slopes):
    # Compare the female and male slopes within each country vi a paired t-test
    t_statistic, p_value = stats.ttest_rel(slopes["female_slope"],slopes["male_slope"])
    print("\nPaired t-test results")
    print("T-statistic:", round(t_statistic, 3))
    #p value is extremely small and then only <0.001 is printed, otherwise the p values is rounded to three decimal points
    print("P-value:", "< 0.001" if p_value < 0.001 else round(p_value, 3))
    return t_statistic, p_value

def run_decline_t_tests(slopes):
    # One-sample t-test per sex: is the mean country slope different from 0 (no decline)?
    for sex in ["female", "male"]:
        t_statistic, p_value = stats.ttest_1samp(slopes[f"{sex}_slope"], 0)
        print(f"\n{sex.capitalize()} slope vs. 0")
        print("T-statistic:", round(t_statistic, 3))
        print("P-value:", "< 0.001" if p_value < 0.001 else round(p_value, 3))

####### Plots ##########
def plot_prevalence(yearly):
    # Plot the average smoking prevalence over time
    #plotting the female mean across all countries over time/year
    plt.plot(yearly["year"], yearly["female_mean"], label="Females", color="#b033d6")
    #95% CI of the mean (mean ± 1.96 × SE)
    plt.fill_between(yearly["year"],yearly["female_mean"] - 1.96 * yearly["female_se"],yearly["female_mean"] + 1.96 * yearly["female_se"],color="#b033d6", alpha=0.2, label="Females: 95% CI of mean", zorder=3)
    #plotting the male mean across all countries in smokin prevalence, plus line color
    plt.plot(yearly["year"], yearly["male_mean"], label="Males", color="#19c219")
    plt.fill_between(yearly["year"],yearly["male_mean"] - 1.96 * yearly["male_se"],yearly["male_mean"] + 1.96 * yearly["male_se"],color="#19c219", alpha=0.2, label="Males: 95% CI of mean", zorder=3)
    #makes title, axes laels, legend and saves the figure to the previously made output folder
    plt.title("Daily Smoking Prevalence, 1980–2012")
    plt.xlim(1980, 2012)
    plt.xlabel("Year")
    plt.ylabel("Prevalence (%)")
    plt.legend()
    plt.savefig(f"{output_folder}/prevalence_over_time.png", dpi=300)
    plt.show()

def plot_relative_decline(relative):
    # Plot relative decline in prevalence using each sexes mean 1980 value across the countries as a baseline 
    female_baseline = relative["female_mean"].iloc[0]
    male_baseline = relative["male_mean"].iloc[0]
    # female relative line plus the shaded area described in fill_between that shows the confidence interval of the data
    plt.plot(relative["year"], relative["female_relative"], label="Females", color="#b033d6")
    plt.fill_between(relative["year"], (relative["female_mean"] - 1.96 * relative["female_se"] - female_baseline) / female_baseline * 100, (relative["female_mean"] + 1.96 * relative["female_se"] - female_baseline) / female_baseline * 100, color="#b033d6", alpha=0.2, label="Females: 95% CI of mean", zorder=3)
    
    # male relative line plus confidence interval shaded
    plt.plot(relative["year"], relative["male_relative"], label="Males", color="#19c219")
    plt.fill_between(relative["year"], (relative["male_mean"] - 1.96 * relative["male_se"] - male_baseline) / male_baseline * 100, (relative["male_mean"] + 1.96 * relative["male_se"] - male_baseline) / male_baseline * 100, color="#19c219", alpha=0.2, label="Males: 95% CI of mean", zorder=3)

    #plots grid lines, title, axes labels, legend
    plt.axhline(0, color="black", linewidth=1, linestyle="-") #added zero line, showing no change since 1980 as a point of reference
    plt.xlim(1980, 2012)
    plt.title("Relative Decline in Daily Smoking Prevalence, 1980–2012\n(% change from each sex's own 1980 level)")
    plt.xlabel("Year")
    plt.ylabel("Change from 1980 (%)")
    plt.legend()
    #saves the figure in the previously generated output folder
    plt.savefig(f"{output_folder}/relative_decline.png", dpi=300)
    plt.show()

def plot_slope_distribution(slopes):
    # list with the female and male slopes, one value per country
    data = [slopes["female_slope"], slopes["male_slope"]]

    # makes box plot, the box itself is the middle 50% of the countries, the line through the box is the median
    box = plt.boxplot(data, widths=0.5, patch_artist=True, showfliers=False)
    for patch, color in zip(box["boxes"], ["#b033d6", "#19c219"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.3) #make the color more transparent
    for median in box["medians"]:
        median.set_color("black") #median line is black

    # one dot per country, spread out sideways a little so they don't overlap
    for position, values in enumerate(data, start=1):
        x_values = np.random.normal(position, 0.06, len(values)) #scatters the dots so they dont overlap
        plt.scatter(x_values, values, color="black", alpha=0.3, s=8, zorder=3, label="One dot = one country" if position == 1 else None) 

    #add a label for the median line in both boxes
    box["medians"][0].set_label("Median")

    plt.axhline(0, color="black", linestyle="--")  # 0 = no change since 1980, line for reference
    plt.xticks([1, 2], ["Females", "Males"])
    plt.ylabel("Relative slope (% of 1980 level per year)")
    plt.title("Decline Rate per Country, by Sex")
    plt.legend()
    plt.savefig(f"{output_folder}/slope_distribution_by_sex.png", dpi=300)    
    plt.show()

def main():
    # Create the output folder
    os.makedirs(output_folder, exist_ok=True)

    # Load and prepare the data
    new_smoking_data = load_data()
    new_smoking_data = clean_data(new_smoking_data)
    #inspect the data
    inspect_data(new_smoking_data)

    # Analyse the data 
    #absolute yearly measn, standarad deviation adn standard error across the countries
    yearly = calculate_yearly_averages(new_smoking_data)
    print()
    print(yearly[["year", "female_mean", "female_sd", "female_se", "male_mean", "male_sd", "male_se"]].round(3).to_string(index=False))
    #has the same means but against a baseline so %change from 1980, so males and females are comparable
    relative = calculate_relative_decline(yearly)
    #calculates the relative slopes, per country and sex
    slopes = calculate_relative_slopes(new_smoking_data)

    # Run the statistical tests
    run_paired_t_test(slopes)
    run_decline_t_tests(slopes)

    # Create the three graphs/plots, two prevalence graphs and the box plot for the slopes
    plot_prevalence(yearly)
    plot_relative_decline(relative)
    plot_slope_distribution(slopes)
    
main()