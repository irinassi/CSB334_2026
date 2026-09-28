#!/usr/bin/env python
# coding: utf-8

# # Normalization of data
# 
# ## When do we normalize and when do we standardize? 
# 
# **Normalization**: when you want to ensure all features are the same scale. (for example, min to max normalization) 
# 
# **Standardization**: when you want to analyze data within different units and/or scales. It ensures features have a mean of 0 and standard deviation of 1 (ensures ALL features are treated equally) 
# 
# 
# <div>
#   <img src="attachment:image.png" width="400">
# </div>
# source: https://www.simplilearn.com/normalization-vs-standardization-article

# ## **Why do we need to know these concepts?**
# 
# - They are used a lot in research. You already did a little bit of normalization in your assignment when you converted your spectra into % instead of looking at raw signal values.
# 
# 
# It helps researchers to compare between different recording days or different mice.

# ## Today we will learn a little bit more about these concepts while doing some pre-processing of fiber photometry signals. 
# 
# ![image.png](attachment:image.png)
# 
# ![image-2.png](attachment:image-2.png)

# <div>
#   <img src="attachment:image.png" width="600">
# </div>
# 
# source: https://link.springer.com/article/10.1007/s43440-024-00646-w

# ## Comprehension question: why do you think we need to pre-process signals? 

# Write your response here

# The fiber photometry processing in the field does not have a clean "one way" standard.
# 
# Most people seem to do whatever is suitable or logical. There are also plenty of programs online that have some processing machinery. 
# 
# 
# Generally, preprocessing typically involves these steps: **filtering, bleaching correction, movement correction, and normalization**

# ![image.png](attachment:image.png)
# 
# https://pmc.ncbi.nlm.nih.gov/articles/PMC10939905/

# In[ ]:


#Loading Necessary Packages
# This is used to access Python interactive environment. This way we can feed input and receive output as we code.
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

import pandas as pd #this package will be used for managing dataframes and excel sheets
import numpy as np  #this package will be used to perform math functions


# In[ ]:


practice = "FP_DATA_UNPROCESSED.xlsx" #inspecting our file 

practicedf = pd....(practice, sheet_name="...") #save excel as a variable
practicedf.head() #inspect first 5 rows
practicedf.tail() #inspect first 5 last


# ## Cleaning Up: Removing Empty Rows

# If you are not sure where your empty cells (NaNs) are, you can simply call: **pd.isna()**
# 
# It checks if a value is “NaN” (Not a Number) or missing/empty.
# 
# Returns:
# 
# - **True** → if the value is missing, empty, or NaN.
# 
# - **False** → if the value is valid (a real number, string, etc.).

# In[ ]:


practicedf....() #checks whether there are any empty observations 


# In[ ]:


practicedf = practicedf....() #dropna removes any rows with NaN values
practicedf.tail()


# ## Renaming our columns

# In[ ]:


practicedf.... = ["time", "isosbestic", "real", "sleep_state"] #change names of all of our columns 
practicedf.head()


# In[ ]:


import scipy as sp 
help(sp)


# ## Converting columns to Numpy Arrays 
# 
# Before doing some math we will convert some of our columns into numpy array. It will save us some headache in the long run! 
# 
# ![image.png](attachment:image.png)
# 
# 

# In[ ]:


#converting our columns into arrays of numbers instead
time = practicedf["time"]....()
isosbestic = practicedf["isosbestic"].to_numpy()
real = practicedf["real"].to_numpy()
time


# ## Understanding our signals 

# The signal in fiber photometry systems decreases over time across repeated exposure to light.(10.1016/j.pbb.2022.173488) 
# 
# Typically, we discard first 10 min of recordings (but could vary by the field) because we want to make sure that fluorescent reached equilibrium and is not affected by me turning it on a few seconds ago for example.
# 
# ![image.png](attachment:image.png)

# In[ ]:


trim_rows = 6000   # 6000 rows * 0.1s per row = 60 seconds
#trimming every variable 
time_sec = time[trim_rows:]
isosbestic_trim = isosbestic[trim_rows:]
real_trim = real[trim_rows:]


# In[ ]:


#making sure all of our variables are the same length
print(len(isosbestic_trim))
print(len(time_sec))
print(len(real_trim))


# ## Curve Fit: Removing fluorescence decay
# 
# Fiber photometry measures changes in fluorescence that reflect
# neuronal activity. However, the fluorescence emitted by
# fluorescent proteins such as GCaMP goes under exponential
# decay when it is stimulated for a long duration of time. Therefore,
# removing this exponential trend is very important and we can do
# this by subtracting the curve of best fit from the fluorescent
# signals.
# 

# In[ ]:


from scipy.stats import zscore
import matplotlib.pyplot as plt


fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

axes[0].plot(time_sec, isosbestic_trim, color="purple")
axes[0].set_ylabel("Isosbestic (unprocessed)")
axes[0].axhline(0, color="gray", linestyle=":", linewidth=1)
axes[0].set_ylim(40, 50) 

axes[1].plot(time_sec, real_trim, color="green")
axes[1].set_ylabel("Real signal (unprocessed)")
axes[1].set_xlabel("Time (seconds)")
axes[1].axhline(0, color="gray", linestyle=":", linewidth=1)
axes[1].set_ylim(125, 160) 

plt.tight_layout()
plt.show()


# ## **Fitting the "correct" curve to the signal**
# 
# Generally, we try to fit double exponential curve because it's flexible enough to capture most photbleaching.
# 
# We need to provide enough flexibility to make sure we preserve the neuronal signal while making sure that both fast decay and slow decay are filtered! 
# 
# ![image.png](attachment:image.png)

# In[2]:


def cf(x, a, b, c, d):
    return a * np.exp(b * x) + c * np.exp(d * x)

 # This function IS the curve shape we're fitting.
    # x = the time values
    # a, b, c, d = the 4 numbers curve_fit will search for
    # a: starting point of the first part of the curve at x[0]
    # b: rate of decay for first part of the curve (generally the fast decay)
    # c: second part of the curve, where slow decay starts 
    # d: decay of "slow curve"


# There are two main ways to do it:
# 
# 1) average all of your signals and find out best curve fit for your data
# 
# OR 
# 
# 2) make an initial curve guess. In this case, I provided a fast/slow bleaching guess
# 
# Obviously, it will be better to fit it against your own data but when you are starting and you dont' have too many experiments you can provide an estimate. 

# In[ ]:


#we're handing the computer four "best guesses" for the four unknowns in our formula
initial_guess_isosbestic = [isosbestic_trim[0], -0.0001, isosbestic_trim[0], -0.000001]
initial_guess_real       = [real_trim[0],       -0.0001, real_trim[0],       -0.000001]


# Documentation: https://docs.scipy.org/doc/scipy-1.2.1/reference/generated/scipy.optimize.curve_fit.html 

# In[ ]:


#finding our curve of best fit
from scipy.optimize import curve_fit
isosbestic_fit_params, _ = curve_fit(
    cf,        # the shape of curve we want
    time_sec,                  # our x values
    isosbestic_trim,            # our y values (what we're trying to match)
    p0=initial_guess_isosbestic,  # our starting guess
    maxfev=20000                # max number of attempts allowed before giving up (default is too low for this data)
)



# In[ ]:


from scipy.optimize import curve_fit
real_fit_params, _ = curve_fit(
    cf,        # the shape of curve we want
    time_sec,                  # our x values
    real_trim,            # our y values (what we're trying to match)
    p0=initial_guess_real,  # our starting guess
    maxfev=20000                # max number of attempts allowed before giving up (default is too low for this data)
)



# ## Substacting the fitted curve to remove photobleaching! 

# In[ ]:


isosbestic_fitted_curve = cf(time_sec, *isosbestic_fit_params) #calling our function
real_fitted_curve = cf(time_sec, *real_fit_params)


# ## Comprehension question: How would you remove the photobleaching? 

# In[ ]:


isosbestic_corr_bleach = 
real_corr_bleach = 


# In[ ]:


print(len(isosbestic_corr_bleach))
print(len(real_corr_bleach))


# In[ ]:


from scipy.stats import zscore
import matplotlib.pyplot as plt


fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

axes[0].plot(time_sec, isosbestic_corr_bleach, color="purple")
axes[0].set_ylabel("Isosbestic (photobleaching removed)")
axes[0].axhline(0, color="gray", linestyle=":", linewidth=1)
axes[0].set_ylim(-1, 2.5) 

axes[1].plot(time_sec, real_corr_bleach, color="green")
axes[1].set_ylabel("Real signal (photobleaching removed)")
axes[1].set_xlabel("Time (seconds)")
axes[1].axhline(0, color="gray", linestyle=":", linewidth=1)

plt.tight_layout()
plt.show()


# ## If our signals are not on the same scale, what can we do to make sure we can compare between animals? 

# Z-score: Two fiber photometry signals has to be standardized,
# meaning
# that the standard deviation = 1 and average = 0.
# 
# This makes the relative pattern of activity easier to compare across animals and recordings, even when their raw fluorescence values are different.
# 
# ![image.png](attachment:image.png)
# 

# In[ ]:


from scipy.stats import zscore #import our zscore function

isosbestic_zscore = ...(isosbestic_corr_bleach)   # calling z-score funcion on both signals
real_zscore = ...(real_corr_bleach)               


# In[ ]:


from scipy.stats import zscore
import matplotlib.pyplot as plt


fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

axes[0].plot(time_sec, isosbestic_zscore, color="purple")
axes[0].set_ylabel("Isosbestic (z-score)")
axes[0].axhline(0, color="gray", linestyle=":", linewidth=1)
axes[0].set_ylim(-3, 5) 


axes[1].plot(time_sec, real_zscore, color="green")
axes[1].set_ylabel("Real signal (z-score)")
axes[1].set_xlabel("Time (seconds)")
axes[1].axhline(0, color="gray", linestyle=":", linewidth=1)

plt.tight_layout()
plt.show()


# ## **Subtracting artifacts from neuronal activity**
# 
# The 465 nm (**"real"**) signal contains the fluorescence changes we want to measure (our neuronal activity), along with unwanted changes caused by movement and gradual leftover fading (decay) of the fluorescence signal. The 405 nm (**isosbestic**) signal helps us estimate these unwanted changes because it is much less sensitive to the neural activity we want to measure.
# 
# First, we use linear regression to scale the 405 nm signal so that its shared changes match those in the 465 nm signal. We then subtract the fitted 405 nm signal from the 465 nm signal. This reduces the shared unwanted changes and leaves a clearer estimate of the activity we want to study.
# 
# ![image.png](attachment:image.png)

# In[ ]:


from scipy.stats import linregress
regression_result = linregress(isosbestic_zscore, real_zscore)
regression_result
p1 = regression_result...       # matches b (slope) in the formula 
p2 = regression_result...   # matches a (intercept) in the formula


# In[ ]:


#use isosbestic signal to predict the "shared artifact" component of real signal 
scaled_isosbestic = (p1 * isosbestic_zscore) + p2 #applying our linear regression 


# ## **Finding Δ F/F (dF/F)** ##
# 
# **Our final value represents neuronal activity** as a change relative to baseline fluorescence (in %): how much the signal goes up or down compared to what it would look like with no activity happening

# In[ ]:


dff = real_zscore - scaled_isosbestic


# In[ ]:


plt.figure(figsize=(10, 4), facecolor='lightblue')   # set figure size and background color
plt.plot(time_sec, dff, color="purple")
plt.ylabel("Neuronal Activity Δ F/F ")
plt.axhline(0, color="gray", linestyle=":", linewidth=1)
plt.tight_layout()
plt.show()


# ## **Cherry on top: Normalizing to max value**
# 
# For simplicity, we sometimes divide the y-scale by the max value so the y-axis reads 0 to 1 — easier to interpret at a glance but some researchers leave it as is. (Depends on the lab)   

# In[ ]:


max_y_value = dff.max()
print("Max y-value used for normalization:", max_y_value)

dFF_final = dff / max_y_value


# In[ ]:


plt.figure(figsize=(10, 4))   # set figure size and background color
plt.plot(time_sec, dFF_final, color="purple")
plt.ylabel("Neuronal Activity Δ F/F ")
plt.axhline(0, color="gray", linestyle=":", linewidth=1)
plt.tight_layout()
plt.show()


# In[ ]:


sleep_state_trim = practicedf["sleep_state"].to_numpy()[trim_rows:]


# In[ ]:


sleep_state_trim


# In[ ]:


photometry_results = pd.DataFrame({
    "time_sec": time_sec,
    "dFF_final": dFF_final,
    "sleep_state": sleep_state_trim,
})

photometry_results


# In[ ]:


photometry_results["dFF_final"] = photometry_results["..."] * 100
photometry_results


# In[ ]:


get_ipython().run_line_magic('store', 'photometry_results #storing the results for analysis in tutorial 5')


# **ShortCut .describe()**: gives you a quick statistical summary for every column of your DataFrame.

# In[ ]:


photometry_results[photometry_results["sleep_state"] == "..."]["dFF_final"].describe()


# In[ ]:


photometry_results[photometry_results["sleep_state"] == "..."]["dFF_final"].describe()


# In[ ]:


fig, ax = plt.subplots(figsize=(14, 4))

# Plot the signal
ax.plot(photometry_results["time_sec"], photometry_results["dFF_final"], color="black", linewidth=0.7)
ax.axhline(0, color="gray", linestyle=":", linewidth=1)

# Shade wherever sleep_state is "R"
ax.fill_between(
    photometry_results["time_sec"],
    ax.get_ylim()[0], ax.get_ylim()[1],
    where=(photometry_results["sleep_state"] == "R"),
    color="red", alpha=0.4
)

ax.set_xlabel("Time (seconds)")
ax.set_ylabel("dF/F")
plt.tight_layout()
plt.show()


# Recommended readings: https://pmc.ncbi.nlm.nih.gov/articles/PMC10939905/
