import numpy as np
import random

# Perform a two-tail bootstrap hypothesis test for the difference in means
def bootstrap(results1, results2, bootstrap_samples=100000):
    # Get the number of students in each group
    N = len(results1)
    M = len(results2)
    
    # Create a universal sample
    universal_sample = results1 + results2
    
    # Count the number of times the difference in means is greater than the observed difference
    count = 0

    # Calculate the observed difference in means
    results1_mean = np.mean(results1)
    results2_mean = np.mean(results2)
    observed_difference = np.mean(results1) - np.mean(results2)
    abs_observed_difference = abs(observed_difference)
    
    # Sample with replacement and calculate the difference in means
    for i in range(bootstrap_samples):
        # Resample the data
        results1_resample = random.choices(universal_sample, k=N) # sample with replacement
        results2_resample = random.choices(universal_sample, k=M) # sample with replacement
        
        # Calculate the mean of the resampled data
        mu_results1 = np.mean(results1_resample)
        mu_results2 = np.mean(results2_resample)
        
        # Calculate the difference in means
        sample_difference = abs(mu_results1 - mu_results2)
        
        # Update the count if the difference in means is greater than the observed difference
        # (which implies that the null hypothesis (no difference) is false)
        if sample_difference > abs_observed_difference:
            count += 1

    pvalue = count / bootstrap_samples

    return results1_mean, results2_mean, pvalue