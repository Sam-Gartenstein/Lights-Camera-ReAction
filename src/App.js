import React, { useState, useEffect } from 'react';
import { 
  Container, 
  TextField, 
  Button, 
  Typography, 
  Box,
  Paper,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Alert,
  Modal
} from '@mui/material';
import LinearProgress from '@mui/material/LinearProgress';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const steps = [
  'API Key',
  'Initializing',
  'Keywords',
  'Confirm Keywords',
  'Sitcom Concept',
  'Outline'
];

const categories = [
  { key: 'setting', label: 'Setting', prompt: 'Enter settings/locations (comma-separated):' },
  { key: 'characters', label: 'Characters', prompt: 'Enter main characters (comma-separated):' },
  { key: 'themes', label: 'Themes', prompt: 'Enter themes/ideas (comma-separated):' },
  { key: 'tone_genre', label: 'Tone/Genre', prompt: 'Enter tone or genre (comma-separated):' }
];

function parseSitcomConcept(concept) {
  // Try to extract the title and description using regex
  const match = concept.match(/Title:\s*"?([^"]+)"?\s*Description:?\s*(.*)/is);
  if (match) {
    return {
      title: match[1].trim(),
      description: match[2].trim()
    };
  }
  // fallback: just return the whole thing as description
  return { title: '', description: concept };
}

function formatOutline(outline) {
  if (!outline) return '';
  // Split into lines
  const lines = outline.split('\n').filter(line => line.trim() !== '');
  const elements = [];
  lines.forEach((line, idx) => {
    if (line.startsWith('Episode Concept:')) {
      elements.push(
        <Typography key={`epconcept-${idx}`} sx={{ mb: 2 }}>
          <b>Episode Concept:</b> {line.replace('Episode Concept:', '').trim()}
        </Typography>
      );
    } else if (line.match(/^Scene \d+:/)) {
      // Split scene number/title from description
      const match = line.match(/^(Scene \d+:\s*"[^"]+"\s*)(.*)/);
      if (match) {
        elements.push(
          <Box key={`scene-${idx}`} sx={{ mb: 2 }}>
            <Typography component="span" sx={{ fontWeight: 'bold' }}>
              {match[1]}
            </Typography>
            <Typography component="span">{match[2]}</Typography>
          </Box>
        );
      } else {
        elements.push(
          <Typography key={`scene-${idx}`} sx={{ mb: 2 }}>
            {line}
          </Typography>
        );
      }
    } else {
      elements.push(
        <Typography key={`other-${idx}`} sx={{ mb: 2 }}>
          {line}
        </Typography>
      );
    }
  });
  return elements;
}

// Helper functions for formatting agent outputs
function splitRecommendations(text) {
  if (!text) return [];
  // Try to split on '- [Suggestion' or '- Suggestion' or numbered list
  let items = text.split(/- \[Suggestion.*?\]:?|\d+\. /g).filter(Boolean);
  if (items.length > 1) return items.map(i => i.trim());
  // Try splitting on '- '
  items = text.split(/- /g).filter(Boolean);
  if (items.length > 1) return items.map(i => i.trim());
  // Fallback: return the whole text as one item
  return [text.trim()];
}

function splitByDash(text) {
  if (!text) return [];
  return text.split(/- /g).filter(Boolean).map(i => i.trim());
}

function splitNumbered(text) {
  if (!text) return [];
  return text.split(/\d+\. /g).filter(Boolean).map(i => i.trim());
}

function App() {
  const [activeStep, setActiveStep] = useState(0);
  const [apiKey, setApiKey] = useState('');
  const [keywords, setKeywords] = useState({
    setting: '',
    characters: '',
    themes: '',
    tone_genre: ''
  });
  const [sitcomConcept, setSitcomConcept] = useState('');
  const [outline, setOutline] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const [validationOpen, setValidationOpen] = useState(false);
  const [validationResult, setValidationResult] = useState('');
  const [validationLoading, setValidationLoading] = useState(false);
  const [sceneFlow, setSceneFlow] = useState(false);
  const [scene1Script, setScene1Script] = useState('');
  const [showOutlineModal, setShowOutlineModal] = useState(false);
  const [showConceptModal, setShowConceptModal] = useState(false);
  const [scene1VectorInfo, setScene1VectorInfo] = useState(null);
  const [scene1VectorLoading, setScene1VectorLoading] = useState(false);
  const [showWritersRoom, setShowWritersRoom] = useState(false);
  const [writersRoomLoading, setWritersRoomLoading] = useState(false);
  const [writersRoomResults, setWritersRoomResults] = useState(null);

  // Generate sitcom concept when landing on the sitcom concept step
  useEffect(() => {
    if (!sceneFlow && activeStep === 4 && !sitcomConcept) {
      generateConcept();
    }
    // eslint-disable-next-line
  }, [activeStep, sceneFlow]);

  // Generate outline when landing on the outline step
  useEffect(() => {
    if (!sceneFlow && activeStep === 5 && !outline) {
      generateOutline();
    }
    // eslint-disable-next-line
  }, [activeStep, sceneFlow]);

  // Generate Scene 1 script when entering scene flow
  useEffect(() => {
    if (sceneFlow && activeStep === 0 && !scene1Script) {
      generateScene1();
    }
    // eslint-disable-next-line
  }, [sceneFlow, activeStep]);

  const generateConcept = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/generate-concept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey, keywords })
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setSitcomConcept(data.concept);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateOutline = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/generate-outline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey, concept: sitcomConcept })
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setOutline(data.outline);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateScene1 = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/generate-scene-1`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey, outline })
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setScene1Script(data.scene1);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const validateOutline = async () => {
    setValidationLoading(true);
    setValidationResult('');
    setValidationOpen(true);
    try {
      const response = await fetch(`${API_BASE_URL}/validate-outline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey, concept: sitcomConcept, outline })
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setValidationResult(data.validation);
    } catch (err) {
      setValidationResult('Error: ' + err.message);
    } finally {
      setValidationLoading(false);
    }
  };

  const handleScene1Validate = async () => {
    setScene1VectorLoading(true);
    setScene1VectorInfo(null);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/scene-1-vector-info`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey, outline, scene1Script })
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setScene1VectorInfo(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setScene1VectorLoading(false);
    }
  };

  const handleWritersRoom = async () => {
    setWritersRoomLoading(true);
    setWritersRoomResults(null);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/scene-1-writers-room`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey, outline })
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setWritersRoomResults(data);
      setShowWritersRoom(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setWritersRoomLoading(false);
    }
  };

  const handleNext = async () => {
    setError('');
    // Simulate initialization
    if (!sceneFlow && activeStep === 1) {
      setProgress(0);
      setLoading(true);
      let value = 0;
      const interval = setInterval(() => {
        value += 10;
        setProgress(value);
        if (value >= 100) {
          clearInterval(interval);
          setLoading(false);
          setActiveStep((prev) => prev + 1);
        }
      }, 100);
      return;
    }
    // Start scene flow after outline
    if (!sceneFlow && activeStep === 5) {
      setSceneFlow(true);
      setActiveStep(0);
      setScene1Script('');
      return;
    }
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setError('');
    if (sceneFlow && activeStep === 0) {
      setSceneFlow(false);
      setActiveStep(5); // Go back to outline step
      return;
    }
    setActiveStep((prev) => prev - 1);
  };

  const handleKeywordChange = (category) => (event) => {
    setKeywords({
      ...keywords,
      [category]: event.target.value
    });
  };

  // Scene stepper
  const sceneSteps = ['Scene 1'];

  const renderStepContent = (step) => {
    if (!sceneFlow) {
      if (step === 0) {
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Enter your OpenAI API Key
            </Typography>
            <TextField
              fullWidth
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              margin="normal"
            />
          </Box>
        );
      }
      if (step === 1) {
        return (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <LinearProgress variant="determinate" value={progress} sx={{ mb: 2 }} />
            <Typography variant="h6">Initializing embedding model and AI agents...</Typography>
          </Box>
        );
      }
      if (step === 2) {
        // All keyword categories on one screen
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Enter Keywords for Your Sitcom
            </Typography>
            {categories.map((cat) => (
              <TextField
                key={cat.key}
                fullWidth
                label={cat.label}
                value={keywords[cat.key]}
                onChange={handleKeywordChange(cat.key)}
                margin="normal"
                helperText={cat.prompt}
                sx={{ mb: 2 }}
              />
            ))}
          </Box>
        );
      }
      if (step === 3) {
        // Confirmation step
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Confirm Your Keywords
            </Typography>
            <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
              {categories.map((cat) => (
                <Box key={cat.key} sx={{ mb: 1 }}>
                  <Typography variant="subtitle1">{cat.label}:</Typography>
                  <Typography>{keywords[cat.key]}</Typography>
                </Box>
              ))}
            </Paper>
          </Box>
        );
      }
      if (step === 4) {
        // Sitcom concept step
        const { title, description } = parseSitcomConcept(sitcomConcept || '');
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Generated Sitcom Concept
            </Typography>
            {loading ? (
              <Box sx={{ textAlign: 'center', py: 6 }}>
                <CircularProgress sx={{ mb: 2 }} />
                <Typography>Generating sitcom concept...</Typography>
              </Box>
            ) : (
              <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
                {title && (
                  <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {title}
                  </Typography>
                )}
                <Typography sx={{ whiteSpace: 'pre-line' }}>
                  {description}
                </Typography>
              </Paper>
            )}
          </Box>
        );
      }
      if (step === 5) {
        // Outline step
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Generated Outline
            </Typography>
            <Button
              variant="outlined"
              sx={{ mb: 2, mr: 2 }}
              onClick={validateOutline}
              disabled={validationLoading || loading}
            >
              {validationLoading ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
              Validate Outline
            </Button>
            <Button
              variant="contained"
              sx={{ mb: 2 }}
              onClick={handleNext}
              disabled={loading}
            >
              Generate Scripts
            </Button>
            <Modal
              open={validationOpen}
              onClose={() => setValidationOpen(false)}
              aria-labelledby="validation-modal-title"
              aria-describedby="validation-modal-description"
            >
              <Box sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                bgcolor: 'background.paper',
                boxShadow: 24,
                p: 4,
                borderRadius: 2,
                minWidth: 300,
                maxWidth: 500
              }}>
                <Typography id="validation-modal-title" variant="h6" gutterBottom>
                  Outline Validation
                </Typography>
                <Typography id="validation-modal-description" sx={{ whiteSpace: 'pre-line' }}>
                  {validationResult}
                </Typography>
                <Box sx={{ mt: 2, textAlign: 'right' }}>
                  <Button onClick={() => setValidationOpen(false)} variant="contained">Close</Button>
                </Box>
              </Box>
            </Modal>
            {loading ? (
              <Box sx={{ textAlign: 'center', py: 6 }}>
                <CircularProgress sx={{ mb: 2 }} />
                <Typography>Generating outline...</Typography>
              </Box>
            ) : (
              <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
                {formatOutline(outline)}
              </Paper>
            )}
          </Box>
        );
      }
    } else {
      // Scene generation flow
      if (step === 0) {
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Scene 1 Script
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Button variant="outlined" onClick={() => setShowOutlineModal(true)}>
                Show Outline
              </Button>
              <Button variant="outlined" onClick={() => setShowConceptModal(true)}>
                Show Concept
              </Button>
            </Box>
            <Modal
              open={showOutlineModal}
              onClose={() => setShowOutlineModal(false)}
              aria-labelledby="outline-modal-title"
              aria-describedby="outline-modal-description"
            >
              <Box sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                bgcolor: 'background.paper',
                boxShadow: 24,
                p: 4,
                borderRadius: 2,
                minWidth: 300,
                maxWidth: 600,
                maxHeight: '80vh',
                overflowY: 'auto'
              }}>
                <Typography id="outline-modal-title" variant="h6" gutterBottom>
                  Full Outline
                </Typography>
                {formatOutline(outline)}
                <Box sx={{ mt: 2, textAlign: 'right' }}>
                  <Button onClick={() => setShowOutlineModal(false)} variant="contained">Close</Button>
                </Box>
              </Box>
            </Modal>
            <Modal
              open={showConceptModal}
              onClose={() => setShowConceptModal(false)}
              aria-labelledby="concept-modal-title"
              aria-describedby="concept-modal-description"
            >
              <Box sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                bgcolor: 'background.paper',
                boxShadow: 24,
                p: 4,
                borderRadius: 2,
                minWidth: 300,
                maxWidth: 600,
                maxHeight: '80vh',
                overflowY: 'auto'
              }}>
                <Typography id="concept-modal-title" variant="h6" gutterBottom>
                  Sitcom Concept
                </Typography>
                {(() => {
                  const { title, description } = parseSitcomConcept(sitcomConcept || '');
                  return <>
                    {title && (
                      <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 1 }}>{title}</Typography>
                    )}
                    <Typography sx={{ whiteSpace: 'pre-line' }}>{description}</Typography>
                  </>;
                })()}
                <Box sx={{ mt: 2, textAlign: 'right' }}>
                  <Button onClick={() => setShowConceptModal(false)} variant="contained">Close</Button>
                </Box>
              </Box>
            </Modal>
            {loading ? (
              <Box sx={{ textAlign: 'center', py: 6 }}>
                <CircularProgress sx={{ mb: 2 }} />
                <Typography>Generating Scene 1 script...</Typography>
              </Box>
            ) : (
              <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
                <Typography sx={{ whiteSpace: 'pre-line' }}>{scene1Script || 'No script generated.'}</Typography>
              </Paper>
            )}
            <Box sx={{ mt: 3, mb: 2, display: 'flex', justifyContent: 'space-between' }}>
              <Button
                variant="contained"
                color="success"
                onClick={handleScene1Validate}
                disabled={scene1VectorLoading || loading}
              >
                {scene1VectorLoading ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
                Validate
              </Button>
              {scene1VectorInfo && !showWritersRoom && (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleWritersRoom}
                  disabled={writersRoomLoading}
                  sx={{ ml: 'auto' }}
                >
                  {writersRoomLoading ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
                  Writer's Room
                </Button>
              )}
            </Box>
            {scene1VectorInfo && (
              <Paper elevation={2} sx={{ p: 2, mt: 2, background: '#f5f5f5' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>Scene 1 Vector DB Info</Typography>
                <Typography><b>Summary:</b> {scene1VectorInfo.summary}</Typography>
                <Typography><b>Characters:</b>{scene1VectorInfo.characters}</Typography>
                <Typography><b>Location:</b> {scene1VectorInfo.location}</Typography>
                <Typography><b>Recurring Joke:</b> {scene1VectorInfo.recurring_joke}</Typography>
                <Typography><b>Emotional Tone:</b> {scene1VectorInfo.emotional_tone}</Typography>
              </Paper>
            )}
            {showWritersRoom && writersRoomResults && (
              <Paper elevation={2} sx={{ p: 3, mt: 3, background: '#e3f2fd' }}>
                <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Writer's Room — Scene 2 Planning
                </Typography>

                {/* Character Agent */}
                <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                  <Typography variant="h6" sx={{ mb: 1 }}>
                    Character Agent
                  </Typography>
                  <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    Consistency:&nbsp;
                    {writersRoomResults.character.is_consistent
                      ? <CheckCircleIcon color="success" fontSize="small" />
                      : <CancelIcon color="error" fontSize="small" />}
                    &nbsp;{writersRoomResults.character.is_consistent ? 'Consistent' : 'Inconsistent'}
                  </Typography>
                  <Typography sx={{ mb: 1 }}>
                    <b>Explanation:</b>
                    <ul style={{ marginTop: 8, marginBottom: 8 }}>
                      {splitNumbered(writersRoomResults.character.explanation).map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </Typography>
                  <Typography sx={{ mb: 1 }}>
                    <b>Recommendations:</b>
                    <ul style={{ marginTop: 8, marginBottom: 8 }}>
                      {splitRecommendations(writersRoomResults.character.recommendations).map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </Typography>
                  <Typography sx={{ mb: 1 }}>
                    <b>Agent's Thoughts:</b>
                    <ul style={{ marginTop: 8, marginBottom: 8 }}>
                      {writersRoomResults.character.thoughts.map((t, i) => <li key={i}>{t}</li>)}
                    </ul>
                  </Typography>
                </Paper>

                {/* Comedic Agent */}
                <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                  <Typography variant="h6" sx={{ mb: 1 }}>
                    Comedic Agent
                  </Typography>
                  <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    Comedic Tone:&nbsp;
                    {writersRoomResults.comedic.is_consistent
                      ? <CheckCircleIcon color="success" fontSize="small" />
                      : <CancelIcon color="error" fontSize="small" />}
                    &nbsp;{writersRoomResults.comedic.is_consistent ? 'Consistent' : 'Inconsistent'}
                  </Typography>
                  <Typography sx={{ mb: 1 }}>
                    <b>Analysis:</b>
                    <ul style={{ marginTop: 8, marginBottom: 8 }}>
                      {splitNumbered(writersRoomResults.comedic.analysis).map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </Typography>
                  <Typography sx={{ mb: 1 }}>
                    <b>Recommendations:</b>
                    <ul style={{ marginTop: 8, marginBottom: 8 }}>
                      {splitRecommendations(writersRoomResults.comedic.recommendations).map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </Typography>
                  <Typography sx={{ mb: 1 }}>
                    <b>Agent's Thoughts:</b>
                    <ul style={{ marginTop: 8, marginBottom: 8 }}>
                      {writersRoomResults.comedic.thoughts.map((t, i) => <li key={i}>{t}</li>)}
                    </ul>
                  </Typography>
                </Paper>

                {/* Environment Agent */}
                <Paper elevation={1} sx={{ p: 2 }}>
                  <Typography variant="h6" sx={{ mb: 1 }}>
                    Environment Agent
                  </Typography>
                  <Typography sx={{ mb: 1 }}>
                    <b>Analysis:</b>
                    <ul style={{ marginTop: 8, marginBottom: 8 }}>
                      {splitByDash(writersRoomResults.environment.analysis).map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </Typography>
                  <Typography sx={{ mb: 1 }}>
                    <b>Transition:</b>
                    <ul style={{ marginTop: 8, marginBottom: 8 }}>
                      {splitByDash(writersRoomResults.environment.transition).map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </Typography>
                  <Typography sx={{ mb: 1 }}>
                    <b>Detail Suggestions:</b>
                    <ul style={{ marginTop: 8, marginBottom: 8 }}>
                      {splitRecommendations(writersRoomResults.environment.details_suggestions).map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </Typography>
                  <Typography sx={{ mb: 1 }}>
                    <b>Agent's Thoughts:</b>
                    <ul style={{ marginTop: 8, marginBottom: 8 }}>
                      {writersRoomResults.environment.thoughts.map((t, i) => <li key={i}>{t}</li>)}
                    </ul>
                  </Typography>
                </Paper>
              </Paper>
            )}
          </Box>
        );
      }
    }
    return null;
  };

  // Validation for keywords step
  const allKeywordsFilled = categories.every(cat => keywords[cat.key].trim() !== '');

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Sitcom Generator
      </Typography>
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {sceneFlow
          ? sceneSteps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))
          : steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
      </Stepper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {renderStepContent(activeStep)}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          disabled={activeStep === 0 || loading}
          onClick={handleBack}
        >
          Back
        </Button>
        {!sceneFlow && (
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={
              loading ||
              (activeStep === 0 && !apiKey) ||
              (activeStep === 4 && loading) ||
              (activeStep === 5 && loading)
            }
          >
            {loading && (activeStep === 1 || activeStep === 4 || activeStep === 5) ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              activeStep === steps.length - 1 ? 'Finish' : 'Next'
            )}
          </Button>
        )}
      </Box>
    </Container>
  );
}

export default App; 