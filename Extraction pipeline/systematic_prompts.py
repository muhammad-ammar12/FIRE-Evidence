from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser





parser = JsonOutputParser()





query= '''Extract the following information from the randomized controlled trial (RCT)
1. **Population (P):**
   - Description of the study setting, including location and social context.
   - Inclusion criteria for participants.
   - Exclusion criteria for participants.
   - Method of recruitment (e.g., phone, mail, clinic patients).
   - Information on whether consent was taken.
   - Total number of participants randomized or total population at the start of the study.
   - Clusters (if applicable), including the number, type, and number of people per cluster.
   - Details of any baseline imbalances.
   - Withdrawals and exclusions during the study period.
   - Demographic information such as age, sex, race/ethnicity.
   - Severity of illness, co-morbidities, and other relevant sociodemographic data.
   - Information on any subgroups measured or reported.
   - Any additional notes related to the study population.

2. **Intervention (I):**
   - Name of the intervention group.
   - Number of participants randomized to this group (specify whether people or clusters).
   - Theoretical basis or key references for the intervention.
   - Detailed description of the intervention (content, dose, components).
   - Duration of the treatment period.
   - Timing of the intervention (e.g., frequency, duration of each episode).
   - Method of delivery (e.g., mechanism, medium, intensity, fidelity).
   - Information about providers (e.g., number, profession, training, ethnicity).
   - Details of any co-interventions.
   - Economic information (e.g., cost of intervention, changes in other costs).
   - Resource requirements (e.g., staff numbers, equipment).
   - Integrity of intervention delivery and participant compliance.

3. **Comparison (C):**
   - Name of the comparison group.
   - Number of participants randomized to this group (specify whether people or clusters).
   - Theoretical basis or key references for the comparison.
   - Detailed description of the comparison (content, dose, components).
   - Duration of the treatment period.
   - Timing of the comparison (e.g., frequency, duration of each episode).
   - Method of delivery (e.g., mechanism, medium, intensity, fidelity).
   - Information about providers (e.g., number, profession, training, ethnicity).
   - Details of any co-interventions.
   - Economic information (e.g., cost of comparison, changes in other costs).
   - Resource requirements (e.g., staff numbers, equipment).
   - Integrity of comparison delivery and participant compliance.

4. **Outcome (O):**
   - Names of all outcomes measured in the study.
   - Time points when outcomes were measured and reported.
   - Detailed definitions of each outcome (including diagnostic criteria).
   - Information on who measured or reported each outcome.
   - Units of measurement for each outcome.
   - Scales used (including upper and lower limits and whether a high or low score is better).
   - Information on whether the outcome measurement tools are validated.
   - Imputation methods for handling missing data.
   - Assumed risk estimates (e.g., baseline risk).
   - Power analysis details (sample size calculation, achieved power level).

Provide detailed responses for each element listed above.'''

outcome_query="""
You are given a Randomized Control Trial that reports on the comparison of an intervention against a control group. In the outcomes section of the trial, details are provided regarding primary outcomes, secondary outcomes, and adverse events. These outcomes are reported at various time points or within specific subgroups, with associated metrics such as event rates or means, and comparative statistics (e.g., relative risk, odds ratios, confidence intervals, p-values).

Your task is to extract the following information:

Outcome Types: Identify the primary, secondary, and adverse event outcomes mentioned in the trial.
Time Points or Subgroups: Note if the outcomes are reported for specific time points (e.g., 6 months, 12 months) or for subgroups (e.g., age groups, gender).
Event Rates or Means: For each outcome, extract the event rates or means for both the intervention and control groups.
Comparative Statistics: Identify the comparative statistics used for the outcome comparison between the intervention and control groups, such as risk ratios, odds ratios, confidence intervals, and p-values.
"""





template_pico ="""
Based on the knowledge provided to you, you are expected to answer the question {context} using the evidence from the available knowledge.
Please structure your response as follows:

1 Methods
Design: e.g Randomized controlled trial or Randomized noninferiority trial
Allocation concealment: Identify evidence of Allocation Concealment, which ensures the person enrolling participants cannot predict group assignment (e.g., using a web-based central randomization system, opaque sealed envelopes, or IVRS). Do not confuse this with randomization or blinding. Provide the exact text describing concealment or state "Not Mentioned." 
Blinding:
Follow-up duration:
Setting: (number of centers)(healthcare setting)(country)
Sample size: e.g 405 women
2 Population Inclusion: Provide a detailed description of the inclusion criteria for the study population.
3 Key Exclusions: Detail the key exclusion criteria that were applied in the study.
4 Intervention: description (n=). Describe the intervention being studied, including details about the type, duration, dosage, and administration method.
5 Comparator: description (n=). Outline the comparator used in the study, including its administration method and relevance to the study.
6 Primary Outcome: List the primary outcome assessed in the study, detailing the measurements.
7 Secondary Outcomes: Provide a detailed list of secondary outcomes assessed in the study.
8 Patient Follow-up: State the follow-up rate and details regarding the analysis.
9 Intention to Treat Analysis: Indicate whether an intention-to-treat analysis was performed. e.g yes or no
10 Baseline Characteristics: Describe the baseline characteristics of the study population, including what is mean age, what is sex distribution, and what is race or ethnicity.
11 Sources of funding: mention any source of funding used in the study. e.g This publication presents independent research commissioned by the National Institute for Health and Care Research
12 Conclusion: Conclude your answer with a direct response to the question posed, summarizing the key findings and how they relate to the question. Do not list any implications of the findings.
"""
pico=PromptTemplate(
    input_variables=["context"],
    template=template_pico

)


template_stat ="""
Extract the outcomes from the outcomes section of the following {context} by strictly following the {format_instructions}. For each outcome, please provide:

Outcome Type: Specify whether the outcome is a primary outcome, secondary outcome, adverse event, or treatment failure (if applicable).
Outcome Description: Provide a brief description of the outcome being measured (e.g., mortality, improvement in symptoms, treatment failure, etc.).
Time Point or Subgroup (if applicable): Mention the time point (e.g., 6 months, 12 months) or the subgroup (e.g., age, gender) if outcomes are reported for specific intervals or groups.
Event Rates or Means:
What is the event rate or mean value for the intervention group?
What is the event rate or mean value for the control group?
Comparison of Outcomes: Provide the comparison between the intervention and control groups using comparative statistics (e.g., risk ratios, odds ratios, confidence intervals, p-values, etc.).
Additionally: If the text includes data on treatment failures, extract and report it explicitly, including any descriptions of treatment failure, event rates or proportions for each group, and relevant comparisons such as hazard ratios or confidence intervals.

Example Response
Outcome Type: Primary Outcome
Outcome Description: Mortality rate at 6 months
Time Point or Subgroup: 6 months
Event Rates or Means:
   Intervention Group: 5%
   Control Group: 7%
Comparison of Outcomes: Relative Risk: 0.71 (95% CI: 0.50-0.94), p = 0.02

Outcome Type: Treatment Failure
Outcome Description: Time to treatment failure
Event Rates or Means:
  Intervention Group: 24.4%
  Control Group: 30.5%
  Comparison of Outcomes: Hazard Ratio: 0.67 (95% CI: 0.44-1.00)

{format_instructions}
{context}


"""
outcomes =PromptTemplate(
    input_variables=["context"],
    template=template_stat,
    partial_variables={"format_instructions": parser.get_format_instructions()},

)