import pandas as pd

# This is the timestamp for when the offical chat logic was merged into production
# The commit hash is 18364046a14a45e5eb52f04a2a834bf391be4b82
# Rounded up to the nearest half hour to accommodate for lag in the deployment.
# Mon Apr 22 13:34:45 2024 -0700
EXPERIMENT_DEPLOYED_TIMESTAMP = pd.Timestamp('2024-04-22 14:00:00.000000-07:00')

END_OF_EXPERIMENT_TIMESTAMP = pd.Timestamp('2024-06-01 00:00:00.000000-07:00')