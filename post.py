def computeDeviceCrossovers(websiteVisits, appVisits):
    # Initialize indices for both visit lists
    i, j = 0, 0
    # Initialize the last device as 'website' if the first visit is from the website, otherwise 'app'
    last_device = None
    switches = 0
    
    # Process both lists together based on their sorted timestamps
    while i < len(websiteVisits) and j < len(appVisits):
        if websiteVisits[i] < appVisits[j]:
            # Check if there's a switch from the last device to 'website'
            if last_device == 'app':
                switches += 1
            # Update last_device and move to the next website visit
            last_device = 'website'
            i += 1
        else:
            # Check if there's a switch from the last device to 'app'
            if last_device == 'website':
                switches += 1
            # Update last_device and move to the next app visit
            last_device = 'app'
            j += 1

    # Process any remaining website visits
    while i < len(websiteVisits):
        if last_device == 'app':
            switches += 1
        last_device = 'website'
        i += 1

    # Process any remaining app visits
    while j < len(appVisits):
        if last_device == 'website':
            switches += 1
        last_device = 'app'
        j += 1

    return switches

# Parsing sample input and output as provided
n = int(input().strip())  # Number of website visits
websiteVisits = [int(input().strip()) for _ in range(n)]

m = int(input().strip())  # Number of app visits
appVisits = [int(input().strip()) for _ in range(m)]

# Output the number of device switches
print(computeDeviceCrossovers(websiteVisits, appVisits))
