library(tidyverse)

#########################
### Data Preparation ###
########################

# Read in data (DeviceCGM takes about 2 mins)
DeviceCGM <- read.table("./study data/DeviceCGM.txt", header = TRUE, sep = "|", fileEncoding = "UTF-16")
VisitInfo <- read.table("./study data/VisitInfo.txt", header = TRUE, sep = "|", fileEncoding = "UTF-16")
PtRoster <- read.table("./study data/PtRoster.txt", header = TRUE, sep = "|", fileEncoding = "UTF-16")

# Makes dates usable in date format (takes about 2 mins)
DeviceCGM <- DeviceCGM %>% 
  mutate(date = as.Date(DeviceDtTm, tz = "UTC")) %>%
  filter(RecordType == "CGM") %>% # removes a tiny percentage of calibration readings (<1%)
  select(PtID, date)

VisitInfo <- VisitInfo %>% 
  mutate(visit_date = as.Date(VisitDt, tz = "UTC"))

# Minimize datasets to only what we need, for simplicity (e.g. CGM patients only, 4/8/16/26-week visits only)
patients_CGM <- (PtRoster %>% filter(TrtGroup == "CGM"))$PtID

patient_visit_dates <- VisitInfo %>%
  filter(PtID %in% patients_CGM) %>%
  filter(Visit %in% c("4 week", "8 week", "16 week", "26 week")) %>%
  arrange(PtID) %>%
  select(PtID, Visit, visit_date)
  
DeviceCGM_min <- DeviceCGM %>%
  filter(PtID %in% patients_CGM)

# Widen patient follow-up visit dates (get data in the format: Patient ID, Wk4 date, Wk8 date, Wk16 date, Wk26 date)
patient_visit_dates_wide <- patient_visit_dates %>%
  spread(Visit, visit_date) %>%
  select("PtID", "4 week", "8 week", "16 week", "26 week") %>%
  rename("wk4" = "4 week", "wk8" = "8 week", "wk16" = "16 week", "wk26" = "26 week")

##############################
### Adherence Calculations ###
##############################

# Join visit dates onto each row of DeviceCGM data
DeviceCGM_min_visits <- DeviceCGM_min %>%
  left_join(patient_visit_dates_wide, by = "PtID")

# If the date of the reading falls within 28 days of the wk X visit date, mark `wkX_check` as TRUE for that reading
DeviceCGM_min_visits <- DeviceCGM_min_visits %>%
  mutate(wk4_check = between(as.numeric(difftime(date, wk4, units = "days")), -28,-1),
         wk8_check = between(as.numeric(difftime(date, wk8, units = "days")), -28, -1),
         wk16_check = between(as.numeric(difftime(date, wk16, units = "days")), -28, -1),
         wk26_check = between(as.numeric(difftime(date, wk26, units = "days")), -28, -1))

# Calculation of visit-specific adherence
  # Count # of distinct dates with a CGM reading, per patient, that fall within the 28-day period before each f/u visit)
wk4_CGMdays_unique <- DeviceCGM_min_visits %>%
  filter(wk4_check == TRUE) %>% # Sum only dates in 28-day window before f/u visit
  group_by(PtID) %>%
  summarise(days_adherent_perc = n_distinct(date) / 28)

wk8_CGMdays_unique <- DeviceCGM_min_visits %>%
  filter(wk8_check == TRUE) %>%
  group_by(PtID) %>%
  summarise(days_adherent_perc = n_distinct(date) / 28)

wk16_CGMdays_unique <- DeviceCGM_min_visits %>%
  filter(wk16_check == TRUE) %>%
  group_by(PtID) %>%
  summarise(days_adherent_perc = n_distinct(date) / 28)

wk26_CGMdays_unique <- DeviceCGM_min_visits %>%
  filter(wk26_check == TRUE) %>%
  group_by(PtID) %>%
  summarise(days_adherent_perc = n_distinct(date) / 28)

# Join columns for each visit
CGMdays_unique_perc <- wk4_CGMdays_unique %>%
  full_join(wk8_CGMdays_unique, by = "PtID") %>%
  full_join(wk16_CGMdays_unique, by = "PtID") %>%
  full_join(wk26_CGMdays_unique, by = "PtID") %>%
  arrange(PtID)
colnames(CGMdays_unique_perc) <- c("PtID", "wk4_adherence", "wk8_adherence", "wk16_adherence", "wk26_adherence")

# Where NA in CGMdays_unique_perc, here is the breakdown:
  # PtIDs 156, 28, 65, and 134 legitimately had 0 days of adherence where it says NA (switch to 0)
  # PtIDs 31, 182 and 68 are actually missing a visit date, so no way of calculating adherence there (keep as NA)
# This was inspected informally with the following code:
  # sort(unique((DeviceCGM_min_visits %>% filter(PtID == 68))$date))
  # patient_visit_dates %>% filter(PtID == 68)

CGMdays_unique_perc[which(CGMdays_unique_perc$PtID == 156) , "wk8_adherence"] <- 0 # PtID 156
CGMdays_unique_perc[which(CGMdays_unique_perc$PtID == 28) , "wk26_adherence"] <- 0 # PtID 28
CGMdays_unique_perc[which(CGMdays_unique_perc$PtID == 65) , "wk26_adherence"] <- 0 # PtID 65
CGMdays_unique_perc[which(CGMdays_unique_perc$PtID == 134) , "wk26_adherence"] <- 0 # PtID 134
CGMdays_unique_perc[which(CGMdays_unique_perc$PtID == 134) , "wk8_adherence"] <- 0 # PtID 134

# Calculate Final Average Adherence
CGMdays_unique_perc <- CGMdays_unique_perc %>%
  rowwise() %>%
  mutate(final_adherence = mean(c(wk4_adherence, wk8_adherence, wk16_adherence, wk26_adherence), na.rm = TRUE))

# Overall CGM Adherence Calculations to CSV
write.csv(CGMdays_unique_perc, "Adherence-R.csv", row.names = FALSE)