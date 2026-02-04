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
    const totalSlides = 11;

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

            {/* Slide 4: Prompt - Data Model */}
            <SlideContainer ref={el => slideRefs.current[3] = el}>
                <h2 style={{ fontSize: '50px', fontFamily: theme.fonts.header, marginBottom: '30px' }}>Prompt 1: Data Model Generation</h2>
                <p style={{ fontSize: '24px', marginBottom: '20px' }}>Objective: Generate realistic portfolio & macro data.</p>
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
            </SlideContainer>

            {/* Slide 5: Prompt - PIT Estimators */}
            <SlideContainer ref={el => slideRefs.current[4] = el}>
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
            </SlideContainer>

            {/* Slide 6: Prompt - Transition Matrices */}
            <SlideContainer ref={el => slideRefs.current[5] = el}>
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
            </SlideContainer>

            {/* Slide 7: Prompt - Responsible ECL */}
            <SlideContainer ref={el => slideRefs.current[6] = el}>
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
            </SlideContainer>

            {/* Slide 9: Prompt - Report Generation */}
            <SlideContainer ref={el => slideRefs.current[7] = el}>
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
            </SlideContainer>

            {/* Slide 10: Philosophical Aspects */}
            <SlideContainer ref={el => slideRefs.current[8] = el}>
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
            <SlideContainer ref={el => slideRefs.current[9] = el}>
                <h2 style={{ fontSize: '60px', fontFamily: theme.fonts.header }}>About Me</h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '60px', marginTop: '40px' }}>
                    <div style={{ width: '300px', height: '300px', borderRadius: '50%', backgroundColor: '#333', display: 'flex', justifyContent: 'center', alignItems: 'center', border: `4px solid ${theme.colors.tertiary}` }}>
                        <span style={{ color: '#666' }}>[Photo]</span>
                    </div>
                    <div style={{ textAlign: 'left' }}>
                        <h3 style={{ fontSize: '40px', color: theme.colors.tertiary, margin: '0 0 20px 0' }}>[Pavel Mironchyk]</h3>
                        <p style={{ fontSize: '28px' }}>Sub-Area Lead in Retail Credit Risk in Rabobank</p>
                        <p style={{ fontSize: '24px', color: theme.colors.quaternary }}>Passionate about combining classical quantitative finance with modern AI agentic workflows.</p>
                    </div>
                </div>
            </SlideContainer>

        </div>
    );
}

export default App;
