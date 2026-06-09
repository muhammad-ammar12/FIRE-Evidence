import pipeline as pipe

#paste your text here to tansform into FHIR-aligned model
pico_text = """

PICO variables
1. Methods
   - Design: Nationwide, prospective cohort study
   - Allocation concealment: Not applicable (observational study)
   - Blinding: Not applicable
   - Follow-up duration: 1996 to 2021
   - Setting: Nationwide (Denmark)
   - Sample size: 2,025,691 women

2. Population Inclusion
   - Women aged 15-49 years residing in Denmark with no history of arterial or venous thrombosis, cancer (except non-melanoma skin cancer),
thrombophilia, liver disease, kidney disease, use of antipsychotics, infertility treatment, hormone therapy use, oophorectomy, hysterectomy,
polycystic ovary syndrome, and endometriosis.

3. Key Exclusions
   - Excluded if they had a history of arterial or venous thrombosis, cancer (except non-melanoma skin cancer), thrombophilia, liver disease, kidney
disease, use of antipsychotics, infertility treatment, hormone therapy use, oophorectomy, hysterectomy, polycystic ovary syndrome, endometriosis, or
had undergone hysterectomy or oophorectomy.

4. Intervention
   - Description: Use of contemporary hormonal contraceptives, including combined oral contraceptives, vaginal ring, patch, progestin-only pills,
subcutaneous implant, and intrauterine devices.

5. Comparator
   - Description: No use of hormonal contraception.

6. Primary Outcome
   - First-time diagnosis of ischaemic stroke or myocardial infarction at discharge.

7. Secondary Outcomes
   - Not explicitly mentioned in the provided text.

8. Patient Follow-up
   - Follow-up rate and details regarding the analysis are not explicitly mentioned, but the study followed women from 1996 to 2021, contributing
22,209,697 person-years of follow-up.

9. Intention to Treat Analysis
   - Not applicable (observational study).

10. Baseline Characteristics
    - Mean age: Not explicitly mentioned, but age range was 15-49 years.
    - Sex distribution: Female only.
    - Race or ethnicity: Not mentioned.

11. Sources of funding
    - The study was supported by Sygeforsikringen “Danmark” (grant 2021-0128).

12. Conclusion
    - The study found that contemporary oestrogen-progestin and progestin-only contraceptives, except for the levonorgestrel-releasing intrauterine
device, were associated with an increased risk of ischaemic stroke and, in some cases, myocardial infarction.
Main results (Stats)
```json
[
  {
    "Outcome Type": "Primary Outcome",
    "Outcome Description": "Ischaemic stroke incidence",
    "Event Rates or Means": {
      "Intervention Group (Combined Oral Contraceptives)": "39 per 100,000 person years (95% CI: 36 to 42)",
      "Control Group (No use of hormonal contraception)": "18 per 100,000 person years (95% CI: 18 to 19)"
    },
    "Comparison of Outcomes": {
      "Adjusted Incidence Rate Ratio": "2.0 (95% CI: 1.9 to 2.2)",
      "Standardised Incidence Rate Difference": "21 extra strokes per 100,000 person years (95% CI: 18 to 24)"
    }
  },
  {
    "Outcome Type": "Primary Outcome",
    "Outcome Description": "Myocardial infarction incidence",
    "Event Rates or Means": {
      "Intervention Group (Combined Oral Contraceptives)": "18 per 100,000 person years (95% CI: 16 to 20)",
      "Control Group (No use of hormonal contraception)": "8 per 100,000 person years (95% CI: 8 to 9)"
    },
    "Comparison of Outcomes": {
      "Adjusted Incidence Rate Ratio": "2.0 (95% CI: 1.7 to 2.2)",
      "Standardised Incidence Rate Difference": "10 extra myocardial infarctions per 100,000 person years (95% CI: 7 to 12)"
    }
  },
  {
    "Outcome Type": "Secondary Outcome",
    "Outcome Description": "Ischaemic stroke incidence with Progestin-only oral contraceptives",
    "Event Rates or Means": {
      "Intervention Group (Progestin-only pills)": "33 per 100,000 person years (95% CI: 25 to 44)",
      "Control Group (No use of hormonal contraception)": "18 per 100,000 person years (95% CI: 18 to 19)"
    },
    "Comparison of Outcomes": {
      "Adjusted Incidence Rate Ratio": "1.6 (95% CI: 1.3 to 2.0)",
      "Standardised Incidence Rate Difference": "15 extra strokes per 100,000 person years (95% CI: 6 to 24)"
    }
  },
  {
    "Outcome Type": "Secondary Outcome",
    "Outcome Description": "Myocardial infarction incidence with Progestin-only oral contraceptives",
    "Event Rates or Means": {
      "Intervention Group (Progestin-only pills)": "13 per 100,000 person years (95% CI: 8 to 19)",
      "Control Group (No use of hormonal contraception)": "8 per 100,000 person years (95% CI: 8 to 9)"
    },
    "Comparison of Outcomes": {
      "Adjusted Incidence Rate Ratio": "1.5 (95% CI: 1.1 to 2.1)",
      "Standardised Incidence Rate Difference": "4 extra myocardial infarctions per 100,000 person years (95% CI: -1 to 9)"
    }
  },
  {
    "Outcome Type": "Adverse Event",
    "Outcome Description": "Ischaemic stroke incidence with Combined Vaginal Ring",
    "Event Rates or Means": {
      "Intervention Group (Vaginal Ring)": "46 per 100,000 person years (95% CI: 25 to 78)",
      "Control Group (No use of hormonal contraception)": "18 per 100,000 person years (95% CI: 18 to 19)"
    },
    "Comparison of Outcomes": {
      "Adjusted Incidence Rate Ratio": "2.4 (95% CI: 1.5 to 3.7)",
      "Standardised Incidence Rate Difference": "28 extra strokes per 100,000 person years (95% CI: 4 to 52)"
    }
  },
  {
    "Outcome Type": "Adverse Event",
    "Outcome Description": "Myocardial infarction incidence with Combined Vaginal Ring",
    "Event Rates or Means": {
      "Intervention Group (Vaginal Ring)": "49 per 100,000 person years (95% CI: 11 to 141)",
      "Control Group (No use of hormonal contraception)": "8 per 100,000 person years (95% CI: 8 to 9)"
    },
    "Comparison of Outcomes": {
      "Adjusted Incidence Rate Ratio": "3.8 (95% CI: 2.0 to 7.3)",
      "Standardised Incidence Rate Difference": "41 extra myocardial infarctions per 100,000 person years (95% CI: -14 to 96)"
    }
  }
]
```



"""



if __name__ == "__main__":
    
    

    #code below is FHIR-KM 
    pipe.run_standardization(pico_text=pico_text)

