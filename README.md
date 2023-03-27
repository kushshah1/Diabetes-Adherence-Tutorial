# Diabetes-Adherence-Tutorial
The WISDM study analyzed the effect of CGM (continuous glucose monitoring) vs. BGM (blood glucose monitoring) usage on various clinical outcomes for older adults with type 1 diabetes (T1D). For patients on the CGM arm, blood sugar readings were taken every 5 minutes over a 6 month trial period, with major in-person follow-up visits at the 4-week, 8-week, 16-week, and 26-week marks.

In the [original analysis](https://jamanetwork.com/journals/jama/fullarticle/2767159) of trial data, amongst the various clinical outcomes that were calculated as summarized versions of the CGM data, patient-level adherence to CGM usage was not measured. Patient-level adherence to CGM could be a useful factor in assessing the effectiveness of CGM, in addition to serving as a possible secondary outcome in post-hoc analyses of the data.

*This repository contains a pipeline for calculating CGM adherence for treatment arm participants in the WISDM trial (beginning with raw trial data and converting it into a patient-level summary), with equivalent code in Python (pandas) and R (dplyr). The data is publicly available online, thus the steps of this analysis are reproducible.*

## Purposes of this Repository
1. The primary purpose of this repository is didactic. We convert a real-world, time-series dataset with 10 million observatons into a patient-level summary. Thus, individuals learning Python or R, who are intending to take a step past basic tutorials, can replicate this data processing pipeline (data read-in, date-time conversion, filtering, creating new columns, joining/grouping/summarizing data, outputting to csv) as a learning exercise. This code can also be useful for data scientists proficient in one of the two libraries (pandas or dplyr) who are attempting to learn the other.
2. This code/output can also be used by clinicians who wish to use CGM adherence statistics from the WISDM clinical trial for further analyses.

## Definitions
Given that Dexcom devices store 30 days of blood glucose readings, we define adherence over the 6-month trial period as the *number of days within the 28-day periods prior to the 4-, 8-, 16-, and 26-week follow-up visits in which an individual in the treatment group has a recorded CGM reading*. If a patient is missing a follow-up visit, adherence will be calculated based on the 28-day periods prior to the other visits.

## Data Availability

All data used in this analysis are publicly available through the Jaeb Center for Health Research ([JCHR](https://www.jaeb.org/)) and can be accessed in two ways:
1. Direct link: https://public.jaeb.org/dataset/564
2. Visit https://public.jaeb.org/datasets/diabetes and click `WISDMPublicDataset.zip'

After downloading the data, the files needed are: `DeviceCGM.txt` (CGM readings), `VisitInfo.txt` (follow-up visit dates), `PtRoster.txt` (treatment arm assignments).

## Steps to Reproduce
1. Clone this repository.
2. Create empty folder from the root directory: `/study data`.
3. Download study data, unzip, and copy the 3 necessary text files into the `study data` folder.
4. Run either `adherence.py` or `adherence.R`, which will output a clean patient-level summary.

## Conclusion

I have done my best to ensure that the steps in both the Python and R pipelines are equivalent and produce identical results at each step. However, if you find any inconsistencies or have suggestions to improve the code, feel free to reach out to me at [kushshah@live.unc.edu](mailto:kushshah@live.unc.edu).

## Key Words
Topical: Digital health, mHealth, wearable devices, type 1 diabetes, continuous glucose monitoring, time-series data, big data

Technical: Python, R, pandas, dplyr, datetime
