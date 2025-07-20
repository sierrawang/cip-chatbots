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
        if sample_difference >= abs_observed_difference:
            count += 1

    pvalue = count / bootstrap_samples

    return results1_mean, results2_mean, pvalue

def bootstrap_difference_of_differences(A_men, A_women, B_men, B_women, bootstrap_samples=100000):
    # Get the lengths of each sample
    A_men_N = len(A_men)
    A_women_N = len(A_women)
    B_men_N = len(B_men)
    B_women_N = len(B_women)

    # Construct the universal samples of women and men
    all_women = A_women + B_women
    all_men = A_men + B_men
    
    # 1. Compute the observed difference of differences
    obs_A_diff = np.mean(A_men) - np.mean(A_women)
    obs_B_diff = np.mean(B_men) - np.mean(B_women)
    obs_diff_diff = obs_A_diff - obs_B_diff

    # Count the number of times the difference of differences is greater than the observed difference
    count = 0

    # 2. Bootstrap the difference of differences
    for _ in range(bootstrap_samples):
        # Draw bootstrap samples (with replacement) from each group
        A_women_samp = random.choices(all_women, k=A_women_N)
        A_men_samp = random.choices(all_men, k=A_men_N)

        B_women_samp = random.choices(all_women, k=B_women_N)
        B_men_samp = random.choices(all_men, k=B_men_N)

        # Compute difference for each condition in the bootstrap sample
        A_diff = np.mean(A_men_samp) - np.mean(A_women_samp)
        B_diff = np.mean(B_men_samp) - np.mean(B_women_samp)
        sample_diff = A_diff - B_diff
        
        # Update the count if the difference of differences is greater than the observed difference
        if obs_diff_diff < 0 and sample_diff <= obs_diff_diff:
            count += 1
        elif obs_diff_diff >= 0 and sample_diff >= obs_diff_diff:
            count += 1

    # 3. Calculate p-value
    p_value = count / bootstrap_samples
    
    return obs_A_diff, obs_B_diff, p_value
