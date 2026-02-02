import React from 'react';
import { Deck, Slide, Heading, Text, Image, CodePane, FlexBox, Box } from 'spectacle';

const theme = {
    colors: {
        primary: '#1F2022',
        secondary: '#FFFFFF',
        tertiary: '#03A9FC',
        quaternary: '#CECECE',
    },
    fonts: {
        header: '"Open Sans Condensed", Helvetica, Arial, sans-serif',
        text: '"Open Sans Condensed", Helvetica, Arial, sans-serif',
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

function App() {
    return (
        <Deck theme={theme}>
            <Slide>
                <FlexBox height="100%" flexDirection="column">
                    <Heading margin="0px" fontSize="150px">IFRS9 & CECL</Heading>
                    <Heading margin="0px" color="tertiary" fontSize="100px">Model Synthesis</Heading>
                    <Text>This project is dedicated to synthesis of the reference IFRS9 and CECL models in python using big LLMs.
                        The idea is to synthesize a python framework from scratch that conforms to the regulation. The resulted codes
                        can be regenerated and updated as the regulation changes.
                    </Text>
                </FlexBox>
            </Slide>

            <Slide>
                <FlexBox height="100%" flexDirection="column">
                    <Heading margin="0px 0px 50px 0px" fontSize="h2">Methodology</Heading>
                    <Text>Synthesizing a Python framework from scratch using generative AI.</Text>
                    <Box height="400px" width="800px" style={{ position: 'relative' }}>
                        <Image
                            src="default_simulation_timeline.png"
                            width="100%"
                            height="100%"
                            style={{ objectFit: 'contain' }}
                        />
                    </Box>
                </FlexBox>
            </Slide>

            <Slide>
                <FlexBox height="100%" flexDirection="column" alignItems="center">
                    <Heading margin="0px 0px 20px 0px" fontSize="h2">Core Schema</Heading>
                    <CodePane language="python" highlightRanges={[1, 10]}>
                        {codeSnippet}
                    </CodePane>
                </FlexBox>
            </Slide>

            <Slide>
                <FlexBox height="100%" flexDirection="column">
                    <Heading fontSize="h2">Data Simulation</Heading>
                    <Text>Synthetic data generation for robust model training.</Text>
                    <FlexBox alignItems="start" flexDirection="column">
                        <Text style={{ fontSize: '32px' }}>• Historical Obligor Data (Portfolio)</Text>
                        <Text style={{ fontSize: '32px' }}>• Macroeconomic Scenarios (Base, Optimistic, Pessimistic)</Text>
                        <Text style={{ fontSize: '32px' }}>• Monte Carlo Simulation for Default timelines</Text>
                    </FlexBox>
                </FlexBox>
            </Slide>

            <Slide>
                <FlexBox height="100%" flexDirection="column">
                    <Heading fontSize="h2">Conclusion</Heading>
                    <Text>Next Steps & Future Work</Text>
                    <FlexBox alignItems="start" flexDirection="column">
                        <Text>• Integrate LLM-driven code refinement</Text>
                        <Text>• Expand validation tests</Text>
                        <Text>• Deploy to Cloud (Firebase)</Text>
                    </FlexBox>
                </FlexBox>
            </Slide>
        </Deck>
    );
}

export default App;
