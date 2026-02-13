import React, { useState, useEffect, useRef } from 'react';

const theme = {
    colors: {
        primary: '#1F2022',
        secondary: '#FFFFFF',
        tertiary: '#03A9FC',
        quaternary: '#CECECE',
        codeBg: '#2a2b2e',
    },
    fonts: {
        header: '"Open Sans Condensed", Helvetica, Arial, sans-serif',
        text: '"Open Sans Condensed", Helvetica, Arial, sans-serif',
        mono: '"Fira Code", "Consolas", "Monaco", "Andale Mono", monospace',
    },
};

const codeSnippet = `
@dataclass
class IFRS9DataSchema:
    """Schema constants for IFRS9 data"""
    DATE = 'date'
    OBLIGOR_ID = 'obligor_id'
    SEGMENT = 'segment'
    PRODUCT = 'product'
    EXPOSURE = 'exposure'
    DRAWN_AMOUNT = 'drawn_amount'
    DPD = 'dpd' # Days Past Due
    INTERNAL_RATING = 'internal_rating'
`.trim();

const SlideContainer = React.forwardRef(({ children }, ref) => (
    <div ref={ref} style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '40px',
        boxSizing: 'border-box',
        borderBottom: '1px solid #333'
    }}>
        <div style={{ maxWidth: '1200px', width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            {children}
        </div>
    </div>
));

const CodeBlock = ({ code }) => (
    <div style={{
        backgroundColor: theme.colors.codeBg,
        padding: '20px',
        borderRadius: '8px',
        width: '100%',
        overflowX: 'auto',
        boxShadow: '0 4px 6px rgba(0,0,0,0.3)',
        border: `1px solid ${theme.colors.quaternary}33`
    }}>
        <pre style={{ margin: 0, fontFamily: theme.fonts.mono, fontSize: '18px', whiteSpace: 'pre-wrap', color: '#a9b7c6' }}>
            <code>{code}</code>
        </pre>
    </div>
);

function App() {
    const [currentSlide, setCurrentSlide] = useState(0);
    const slideRefs = useRef([]);
    const totalSlides = 15;

    useEffect(() => {
        // Initialize refs array
        slideRefs.current = slideRefs.current.slice(0, totalSlides);
    }, []);

    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === ' ') {
                e.preventDefault();
                setCurrentSlide((prev) => Math.min(prev + 1, totalSlides - 1));
            } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
                e.preventDefault();
                setCurrentSlide((prev) => Math.max(prev - 1, 0));
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    useEffect(() => {
        if (slideRefs.current[currentSlide]) {
            slideRefs.current[currentSlide].scrollIntoView({ behavior: 'smooth' });
        }
    }, [currentSlide]);

    return (
        <div style={{ backgroundColor: theme.colors.primary, color: theme.colors.secondary, fontFamily: theme.fonts.text }}>

            {/* Slide 1: Title */}
            <SlideContainer ref={el => slideRefs.current[0] = el}>
                <h1 style={{ margin: '0', fontSize: '100px', fontFamily: theme.fonts.header, textAlign: 'center' }}>IFRS9 & CECL</h1>
                <h2 style={{ margin: '0', color: theme.colors.tertiary, fontSize: '60px', fontFamily: theme.fonts.header, textAlign: 'center' }}>Model Synthesis</h2>
                <p style={{ fontSize: '24px', textAlign: 'center', maxWidth: '800px', margin: '40px 0' }}>
                    This project is dedicated to synthesis of the reference IFRS9 and CECL models in python using big LLMs.
                    The idea is to synthesize a python framework from scratch that conforms to the regulation. The resulted codes
                    can be regenerated and updated as the regulation changes.
                </p>
            </SlideContainer>

            {/* Slide 2: Revolution in Coding */}
            <SlideContainer ref={el => slideRefs.current[1] = el}>
                <h2 style={{ fontSize: '60px', fontFamily: theme.fonts.header, color: theme.colors.tertiary }}>Agentic Coding Revolution</h2>
                <div style={{ maxWidth: '900px', textAlign: 'left' }}>
                    <p style={{ fontSize: '32px', marginBottom: '40px' }}>
                        Software development is shifting from <b>writing code</b> to <b>orchestrating logic</b>.
                    </p>
                    <ul style={{ fontSize: '28px', lineHeight: '1.6' }}>
                        <li><b>Traditional:</b> Developer writes every line, searches StackOverflow, debugs manually.</li>
                        <li><b>Agentic:</b> Developer defines <i>intent</i> and <i>constraints</i> (Workflows).</li>
                        <li><b>Outcome:</b> Agents autonomously traverse the solution space, implementing complex standards like IFRS9.</li>
                    </ul>
                </div>
            </SlideContainer>

            {/* Slide 3: LLM Synthesis vs Retrieval */}
            <SlideContainer ref={el => slideRefs.current[2] = el}>
                <h2 style={{ fontSize: '60px', fontFamily: theme.fonts.header, color: theme.colors.tertiary }}>Synthesis vs Retrieval</h2>
                <div style={{ maxWidth: '900px', textAlign: 'left' }}>
                    <p style={{ fontSize: '32px' }}>
                        LLMs do not just "search and copy". They <b>synthesize</b>.
                    </p>
                    <div style={{ display: 'flex', gap: '40px', marginTop: '40px' }}>
                        <div style={{ flex: 1, padding: '20px', border: `1px solid ${theme.colors.quaternary}` }}>
                            <h3 style={{ color: theme.colors.tertiary }}>Retrieval (Search)</h3>
                            <p>Query: "IFRS9 PD Formula"</p>
                            <p>Result: Returns a static formula found on a website.</p>
                        </div>
                        <div style={{ flex: 1, padding: '20px', border: `1px solid ${theme.colors.tertiary}` }}>
                            <h3 style={{ color: theme.colors.tertiary }}>Synthesis (LLM)</h3>
                            <p><b>Weights + Context = New Knowledge</b></p>
                            <p>It understands "Risk", "Regulation", and "Python" separately, and <i>fuses</i> them to create a compliant PD engine that never existed before.</p>
                        </div>
                    </div>
                </div>
            </SlideContainer>

            {/* Slide: Agentic Creation */}
            <SlideContainer ref={el => slideRefs.current[3] = el}>
                <h2 style={{ fontSize: '60px', fontFamily: theme.fonts.header, color: theme.colors.tertiary, marginBottom: '30px' }}>Agentic Creation of ECL Framework</h2>
                <div style={{ maxWidth: '900px', textAlign: 'center' }}>
                    <p style={{ fontSize: '32px', marginBottom: '40px' }}>
                        The following prompts facilitated the construction of the Python framework found in this repository.
                    </p>
                    <a href="https://github.com/pamiro/ExpectedLoss" style={{ fontSize: '28px', color: theme.colors.tertiary, textDecoration: 'none', borderBottom: `2px solid ${theme.colors.tertiary}` }}>
                        View Repository on GitHub
                    </a>
                </div>
            </SlideContainer>

            {/* Slide: The Agent */}
            <SlideContainer ref={el => slideRefs.current[4] = el}>
                <h2 style={{ fontSize: '60px', fontFamily: theme.fonts.header, color: theme.colors.tertiary, marginBottom: '30px' }}>The Agent: IFRS9 Model Developer</h2>
                <div style={{ maxWidth: '1000px', textAlign: 'left' }}>
                    <p style={{ fontSize: '28px', marginBottom: '30px' }}>
                        A specialized workflow designed to autonomously execute the Model Development Lifecycle.
                    </p>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
                        <div style={{ padding: '20px', border: `1px solid ${theme.colors.quaternary}` }}>
                            <h3 style={{ color: theme.colors.tertiary, margin: '0 0 15px 0' }}>Planning & Analysis</h3>
                            <ul style={{ fontSize: '22px', lineHeight: '1.5' }}>
                                <li><b>Regulatory Scan:</b> IFRS9, ECB Guidelines, EBA RTS.</li>
                                <li><b>Data Assessment:</b> Quality checks, Segmentation.</li>
                            </ul>
                        </div>
                        <div style={{ padding: '20px', border: `1px solid ${theme.colors.tertiary}` }}>
                            <h3 style={{ color: theme.colors.tertiary, margin: '0 0 15px 0' }}>Execution</h3>
                            <ul style={{ fontSize: '22px', lineHeight: '1.5' }}>
                                <li><b>Modelling:</b> PIT/TTC PD, LGD, EAD.</li>
                                <li><b>Calculation:</b> ECL Engine, Scenarios.</li>
                                <li><b>Validation:</b> Backtesting, Reports.</li>
                            </ul>
                        </div>
                    </div>
                    <div style={{ marginTop: '30px', textAlign: 'center' }}>
                        <a href="https://github.com/pamiro/ExpectedLoss/blob/main/.agent/workflows/ifrs9-model-development.md" style={{ fontSize: '24px', color: theme.colors.tertiary, textDecoration: 'none', borderBottom: `1px solid ${theme.colors.tertiary}` }}>
                            View Agent Workflow: ifrs9-model-development.md
                        </a>
                    </div>
                </div>
            </SlideContainer>

            {/* Slide: The Validator */}
            <SlideContainer ref={el => slideRefs.current[5] = el}>
                <h2 style={{ fontSize: '60px', fontFamily: theme.fonts.header, color: theme.colors.tertiary, marginBottom: '30px' }}>The Agent: IFRS9 Model Validator</h2>
                <div style={{ maxWidth: '1000px', textAlign: 'left' }}>
                    <p style={{ fontSize: '28px', marginBottom: '30px' }}>
                        An independent adversarial agent designed to challenge the model and ensure compliance.
                    </p>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
                        <div style={{ padding: '20px', border: `1px solid ${theme.colors.quaternary}` }}>
                            <h3 style={{ color: theme.colors.tertiary, margin: '0 0 15px 0' }}>Independent Review</h3>
                            <ul style={{ fontSize: '22px', lineHeight: '1.5' }}>
                                <li><b>Governance:</b> Challenge assumptions & methodology.</li>
                                <li><b>Compliance:</b> Check against EBA Guidelines / ECB Guide.</li>
                            </ul>
                        </div>
                        <div style={{ padding: '20px', border: `1px solid ${theme.colors.tertiary}` }}>
                            <h3 style={{ color: theme.colors.tertiary, margin: '0 0 15px 0' }}>Key Checks</h3>
                            <ul style={{ fontSize: '22px', lineHeight: '1.5' }}>
                                <li><b>Backtesting:</b> Binomial tests, PSI.</li>
                                <li><b>Sensitivity:</b> Stress testing scenarios.</li>
                                <li><b>Benchmarking:</b> Compare against challenger models.</li>
                            </ul>
                        </div>
                    </div>
                    <div style={{ marginTop: '30px', textAlign: 'center' }}>
                        <a href="https://github.com/pamiro/ExpectedLoss/blob/main/.agent/workflows/ifrs9-cecl-validation.md" style={{ fontSize: '24px', color: theme.colors.tertiary, textDecoration: 'none', borderBottom: `1px solid ${theme.colors.tertiary}` }}>
                            View Agent Workflow: ifrs9-cecl-validation.md
                        </a>
                    </div>
                </div>
            </SlideContainer>

            {/* Slide 4: Prompt - Data Model */}
            <SlideContainer ref={el => slideRefs.current[6] = el}>
                <h2 style={{ fontSize: '50px', fontFamily: theme.fonts.header, marginBottom: '30px' }}>Prompt 1: Data Model Generation</h2>
                <p style={{ fontSize: '24px', marginBottom: '20px' }}>Objective: Generate portfolio & macro data.</p>
                <div style={{ width: '100%', maxWidth: '1000px' }}>
                    <CodeBlock code={`
@[/ifrs9-model-development]
Create file data_model.py that generates 20 years history for:
- Retail consumer loans (short term)
- Private individual mortgages
- SME loans
Include simulated data for macroeconomic history (GDP, Unemployment) and projections (Base, Optimistic, Pessimistic).
                    `.trim()} />
                </div>
                <div style={{ marginTop: '30px', maxWidth: '1000px', textAlign: 'left', borderLeft: `4px solid ${theme.colors.tertiary}`, paddingLeft: '20px' }}>
                    <h3 style={{ color: theme.colors.tertiary, margin: '0 0 10px 0' }}>Generated Code: data_model.py</h3>
                    <p style={{ fontSize: '22px' }}>
                        Synthesized a robust IFRS9 compliant data generator using PySpark. It creates realistic macro-economic scenarios (GDP, Unemployment) and a synthetic portfolio of obligors with history, enabling stress testing.
                    </p>
                </div>
            </SlideContainer>

            {/* Slide 5: Prompt - PIT Estimators */}
            <SlideContainer ref={el => slideRefs.current[7] = el}>
                <h2 style={{ fontSize: '50px', fontFamily: theme.fonts.header, marginBottom: '30px' }}>Prompt 2: PIT PD/LGD/EAD</h2>
                <p style={{ fontSize: '24px', marginBottom: '20px' }}>Objective: Convert TTC parameters to Point-in-Time.</p>
                <div style={{ width: '100%', maxWidth: '1000px' }}>
                    <CodeBlock code={`
@[/ifrs9-model-development]
Create pd_pit_model.py.
Implement a Vasicek Single Factor model to convert Through-the-Cycle (TTC) PDs to Point-in-Time (PIT) PDs.
- Link the "Z-factor" to the macroeconomic variables defined in the data model.
- Apply similar macro-conditioning to LGD (Downturn LGD) and EAD.
                    `.trim()} />
                </div>
                <div style={{ marginTop: '30px', maxWidth: '1000px', textAlign: 'left', borderLeft: `4px solid ${theme.colors.tertiary}`, paddingLeft: '20px' }}>
                    <h3 style={{ color: theme.colors.tertiary, margin: '0 0 10px 0' }}>Generated Code: pd_pit_model.py</h3>
                    <p style={{ fontSize: '22px' }}>
                        Implemented a Vasicek Single Factor Model to bridge the gap between Through-the-Cycle (TTC) and Point-in-Time (PIT) PDs. It dynamically adjusts risk parameters based on the Z-factors derived from macro data.
                    </p>
                </div>
            </SlideContainer>

            {/* Slide 6: Prompt - Transition Matrices */}
            <SlideContainer ref={el => slideRefs.current[8] = el}>
                <h2 style={{ fontSize: '50px', fontFamily: theme.fonts.header, marginBottom: '30px' }}>Prompt 3: Transition Matrices</h2>
                <p style={{ fontSize: '24px', marginBottom: '20px' }}>Objective: Markov Chain implementation for Lifetime PD.</p>
                <div style={{ width: '100%', maxWidth: '1000px' }}>
                    <CodeBlock code={`
@[/ifrs9-model-development]
Create transition_matrix.py.
- Implement logic to estimate yearly Transition Matrices (Migration between Rating Grades).
- Ensure matrices are conditioned on the economic cycle (shift downgrade probs in recession).
- Implement multi-period multiplication M(0,T) to derive Cumulative PD curves.
                    `.trim()} />
                </div>
                <div style={{ marginTop: '30px', maxWidth: '1000px', textAlign: 'left', borderLeft: `4px solid ${theme.colors.tertiary}`, paddingLeft: '20px' }}>
                    <h3 style={{ color: theme.colors.tertiary, margin: '0 0 10px 0' }}>Generated Code: transition_matrix.py</h3>
                    <p style={{ fontSize: '22px' }}>
                        Estimated yearly Transition Matrices using a matrix multiplication approach. The logic conditions migration probabilities on the economic cycle, ensuring higher downgrade risks during recessions.
                    </p>
                </div>
            </SlideContainer>

            {/* Slide 7: Prompt - Responsible ECL */}
            <SlideContainer ref={el => slideRefs.current[9] = el}>
                <h2 style={{ fontSize: '50px', fontFamily: theme.fonts.header, marginBottom: '30px' }}>Prompt 4: ECL Engine</h2>
                <p style={{ fontSize: '24px', marginBottom: '20px' }}>Objective: The "Responsible" Calculation Engine.</p>
                <div style={{ width: '100%', maxWidth: '1000px' }}>
                    <CodeBlock code={`
@[/ifrs9-model-development]
Create ecl_engine.py.
- Implement the 3-Stage Impairment Model (Stage 1: 12m, Stage 2/3: Lifetime).
- Calculate ECL = Sum(PD_t * LGD_t * EAD_t * DiscountFactor_t).
- Ensure "Unbiased" estimate by probability-weighting the 3 macro scenarios (40/30/30).
                    `.trim()} />
                </div>
                <div style={{ marginTop: '30px', maxWidth: '1000px', textAlign: 'left', borderLeft: `4px solid ${theme.colors.tertiary}`, paddingLeft: '20px' }}>
                    <h3 style={{ color: theme.colors.tertiary, margin: '0 0 10px 0' }}>Generated Code: ecl_engine.py</h3>
                    <p style={{ fontSize: '22px' }}>
                        Constructed a 3-Stage Impairment Engine. It calculates 12-month ECL for Stage 1 and Lifetime ECL for Stage 2/3, applying probability weights to multiple forward-looking scenarios.
                    </p>
                </div>
            </SlideContainer>

            {/* Slide 9: Prompt - Report Generation */}
            <SlideContainer ref={el => slideRefs.current[10] = el}>
                <h2 style={{ fontSize: '50px', fontFamily: theme.fonts.header, marginBottom: '30px' }}>Prompt 5: Reporting & Analysis</h2>
                <p style={{ fontSize: '24px', marginBottom: '20px' }}>Objective: End-to-end execution and visualization.</p>
                <div style={{ width: '100%', maxWidth: '1000px' }}>
                    <CodeBlock code={`
@[/ifrs9-model-development]
Create run_analysis.py.
- Load the synthetic data from data_model.py.
- Run the PIT estimators and Transition Matrix logic.
- Calculate final ECL for the portfolio.
- Generate a summary report (Markdown/PDF) comparing Stage 1 vs Stage 2 ECL and visualising the impact of the "Pessimistic" scenario.
                    `.trim()} />
                </div>
                <div style={{ marginTop: '30px', maxWidth: '1000px', textAlign: 'left', borderLeft: `4px solid ${theme.colors.tertiary}`, paddingLeft: '20px' }}>
                    <h3 style={{ color: theme.colors.tertiary, margin: '0 0 10px 0' }}>Generated Code: run_analysis.py</h3>
                    <p style={{ fontSize: '22px' }}>
                        Orchestrated the entire pipeline. This script loads data, executes models, calculates final provisions, and auto-generates a comprehensive Markdown validation report with sensitivity analysis.
                    </p>
                </div>
            </SlideContainer>

            {/* Slide: Analysis Report */}
            <SlideContainer ref={el => slideRefs.current[11] = el}>
                <h2 style={{ fontSize: '50px', fontFamily: theme.fonts.header, marginBottom: '30px' }}>Generated Artifact: Analysis Report</h2>
                <div style={{ width: '100%', maxWidth: '1000px', maxHeight: '600px', overflowY: 'auto' }}>
                    <CodeBlock code={`
# IFRS 9 ECL Analysis Report

## Executive Summary
**Total ECL**: €426,914.58
**Total Exposure**: €24,225,701.16
**Coverage Ratio**: 1.76%

---

## 1. Scenario Analysis (Sensitivity)
The impact of the Pessimistic Scenario compared to Base Case:

| Scenario | Total ECL (€) | Δ vs Base |
| :--- | :--- | :--- |
| **Base** | €1,067,286.46 | - |
| **Optimistic** | €1,143,440.92 | 7.1% |
| **Pessimistic** | €1,137,951.93 | **+6.6%** |

> [!WARNING]
> The Pessimistic scenario drives a 6.6% increase in provisions, highlighting sensitivity to Example macro factors (Z-Factor).

---

## 2. Stage Breakdown (Staging)

| Stage | Definition | ECL Amount (€) | % of Total |
| :--- | :--- | :--- | :--- |
| **Stage 1** | Performing (12m ECL) | €218,532.84 | 51.2% |
| **Stage 2** | Underperforming (Lifetime) | €0.00 | 0.0% |
| **Stage 3** | Defaulted (Lifetime) | €208,381.75 | 48.8% |
                    `.trim()} />
                </div>
            </SlideContainer>

            {/* Slide: Validation Report */}
            <SlideContainer ref={el => slideRefs.current[12] = el}>
                <h2 style={{ fontSize: '50px', fontFamily: theme.fonts.header, marginBottom: '30px' }}>Generated Artifact: Validation Report</h2>
                <div style={{ width: '100%', maxWidth: '1000px', maxHeight: '600px', overflowY: 'auto' }}>
                    <CodeBlock code={`
# Model Validation Report: IFRS 9 Framework

## 1. Executive Summary
**Overall Rating**: **AMBER** (Conceptually Sound, Implementation Simplified)

### Key Strengths
*   **Methodological Soundness**: Adoption of the Vasicek Single Factor Model and Markov Chains for Retail/SME portfolios.
*   **IFRS 9 Compliance**: Correct implementation of the 3-Stage Impairment model and Discounting logic.
*   **Scenario Weighting**: Explicit "Unbiased Estimate" calculation using probability-weighted scenarios.

---

## 2. Compliance Assessment (EBA Guidelines)

| EBA Section | Requirement | Compliance Status | Analysis |
| :--- | :--- | :--- | :--- |
| **4.2.1 (17)** | **Validation Process** | ⚠️ **Partial** | Validation logic is manual. No automated backtesting (Binomial tests, PSI). |
| **4.2.3 (25)** | **PD Estimation** | ✅ **Compliant** | pd_pit_model.py correctly links TTC PD to Macro Z-Factors to derive PIT PD. |
| **4.2.4 (30)** | **LGD Estimation** | ⚠️ **Partial** | LGD is adjusted by a scalar. Lack of component-based modelling. |
| **4.3.2 (45)** | **Scenario Selection** | ✅ **Compliant** | ecl_engine.py explicit handles Base, Optimistic, and Pessimistic scenarios. |
| **4.4.1 (55)** | **SICR Assessment** | ⚠️ **Partial** | Implicit bucket approach. Robust quantitative test is not defined as a module. |

---

## 4. Conclusion & Recommendations
1.  **Refine LGD Models**: Replace scalars with structural Workout LGD models.
2.  **Backtesting Module**: Create a new module src/backtesting.py.
3.  **Governance**: Formalize SICR definitions.
                    `.trim()} />
                </div>
            </SlideContainer>

            {/* Slide 10: Philosophical Aspects */}
            <SlideContainer ref={el => slideRefs.current[13] = el}>
                <h2 style={{ fontSize: '60px', fontFamily: theme.fonts.header, color: theme.colors.tertiary }}>Philosophical Aspects</h2>
                <p style={{ fontSize: '32px', fontStyle: 'italic', marginBottom: '40px' }}>"Prediction is very difficult, especially if it's about the future."</p>
                <div style={{ maxWidth: '800px', fontSize: '28px', textAlign: 'left' }}>
                    <p>• <b>Models vs Reality:</b> Are we modelling risk, or just modelling our <i>assumptions</i> about risk?</p>
                    <p>• <b>The Illusion of Precision:</b> Calculating ECL to 2 decimal places when the macro forecast is uncertain.</p>
                    <p>• <b>Ethics:</b> The impact of "Black Box" models on credit access.</p>
                    <p style={{ marginTop: '40px', color: theme.colors.quaternary, fontSize: '24px' }}>(Content to be expanded)</p>
                </div>
            </SlideContainer>

            {/* Slide 11: Bio */}
            <SlideContainer ref={el => slideRefs.current[14] = el}>
                <h2 style={{ fontSize: '60px', fontFamily: theme.fonts.header }}>About Me</h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '60px', marginTop: '40px' }}>
                    <div style={{ width: '300px', height: '300px', borderRadius: '50%', backgroundColor: '#333', display: 'flex', justifyContent: 'center', alignItems: 'center', border: `4px solid ${theme.colors.tertiary}` }}>
                        <img src="/profile.png" alt="Pavel Mironchyk" style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }} />
                    </div>
                    <div style={{ textAlign: 'left' }}>
                        <h3 style={{ fontSize: '40px', color: theme.colors.tertiary, margin: '0 0 20px 0' }}>Pavel Mironchyk</h3>
                        <p style={{ fontSize: '28px' }}>Rabobank</p>
                        <p style={{ fontSize: '24px', color: theme.colors.quaternary }}>Passionate about combining classical quantitative finance with modern AI agentic workflows.</p>
                    </div>
                </div>
            </SlideContainer>

        </div>
    );
}

export default App;
