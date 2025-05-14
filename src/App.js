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
import jsPDF from 'jspdf';

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

  // Find the index of the first line that starts with 'Scene'
  const firstSceneIdx = lines.findIndex(line => line.startsWith('Scene'));
  if (firstSceneIdx === -1) return ''; // No scene found

  const elements = [];
  lines.slice(firstSceneIdx).forEach((line, idx) => {
    if (line.match(/^Scene \d+:/)) {
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
  if (!text || typeof text !== 'string') return [];
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
  if (!text || typeof text !== 'string') return [];
  return text.split(/- /g).filter(Boolean).map(i => i.trim());
}

function splitNumbered(text) {
  if (!text || typeof text !== 'string') return [];
  return text.split(/\d+\. /g).filter(Boolean).map(i => i.trim());
}

// Helper to chunk an array into groups of a given size
function chunkArray(array, size) {
  const result = [];
  for (let i = 0; i < array.length; i += size) {
    result.push(array.slice(i, i + size));
  }
  return result;
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
  const [concept, setConcept] = useState('');
  const [outline, setOutline] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const [validationOpen, setValidationOpen] = useState(false);
  const [validationResult, setValidationResult] = useState('');
  const [validationLoading, setValidationLoading] = useState(false);
  const [sceneFlow, setSceneFlow] = useState(false);
  const [showOutlineModal, setShowOutlineModal] = useState(false);
  const [showConceptModal, setShowConceptModal] = useState(false);
  const [scene1VectorInfo, setScene1VectorInfo] = useState(null);
  const [scene1VectorLoading, setScene1VectorLoading] = useState(false);
  const [showWritersRoom, setShowWritersRoom] = useState({});
  const [writersRoomLoading, setWritersRoomLoading] = useState(false);
  const [writersRoomResultsByScene, setWritersRoomResultsByScene] = useState({});
  const [scene2VectorInfo, setScene2VectorInfo] = useState(null);
  const [scene2VectorLoading, setScene2VectorLoading] = useState(false);
  const [showWritersRoom2, setShowWritersRoom2] = useState(false);
  const [writersRoomLoading2, setWritersRoomLoading2] = useState(false);
  const [writersRoomResults2, setWritersRoomResults2] = useState(null);
  const [showVectorInfo, setShowVectorInfo] = useState(false);
  const [vectorLoading, setVectorLoading] = useState(false);
  const [vectorInfo, setVectorInfo] = useState(null);
  
  // Store all scenes in a single object
  const [scenes, setScenes] = useState({});
  const [vectorInfoByScene, setVectorInfoByScene] = useState({});
  
  // Original steps for concept generation
  const conceptSteps = [
    'API Key',
    'Keywords',
    'Concept',
    'Outline'
  ];

  // Scene steps for script generation
  const sceneSteps = [
    'Scene 1',
    'Scene 2',
    'Scene 3',
    'Scene 4',
    'Scene 5',
    'Scene 6',
    'Scene 7',
    'Scene 8',
    'Scene 9',
    'Scene 10',
    'Scene 11',
    'Scene 12',
    'Scene 13',
    'Scene 14',
    'Scene 15',
    'Scene 16',
    'Scene 17',
    'Scene 18',
    'Scene 19',
    'Scene 20'
  ];

  // Track which flow we're in
  const [currentFlow, setCurrentFlow] = useState('concept'); // 'concept' or 'scenes'

  // Generate sitcom concept when landing on the sitcom concept step
  useEffect(() => {
    if (!sceneFlow && activeStep === 4 && !concept) {
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
    if (sceneFlow && activeStep === 0 && !scenes[1]) {
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
      setConcept(data.concept);
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
        body: JSON.stringify({ apiKey, concept })
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
      setScenes(prev => ({ ...prev, 1: data.scene1 }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateNextScene = async (sceneNumber) => {
    setLoading(true);
    setError('');
    try {
      console.log('Sending request with data:', {
        apiKey,
        outline,
        previousScene: scenes[sceneNumber - 1],
        writersRoomResults: writersRoomResultsByScene[sceneNumber - 1]
      });

      const response = await fetch(`${API_BASE_URL}/generate-scene/${sceneNumber}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          apiKey,
          outline,
          previousScene: scenes[sceneNumber - 1],
          writersRoomResults: writersRoomResultsByScene[sceneNumber - 1]
        })
      });

      const data = await response.json();
      console.log('Received response:', data);

      if (data.error) throw new Error(data.error);
      
      if (!data[`scene${sceneNumber}`]) {
        throw new Error('No scene data received from server');
      }

      setScenes(prev => ({ ...prev, [sceneNumber]: data[`scene${sceneNumber}`] }));
      setActiveStep(sceneNumber - 1); // Adjust activeStep to match scene number
    } catch (err) {
      console.error('Error generating scene:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const validateOutline = async () => {
    setValidationLoading(true);
    setValidationResult('');
    try {
      const response = await fetch(`${API_BASE_URL}/validate-outline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey, concept, outline })
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setValidationResult(data.validation);
      setValidationOpen(true); // <-- Move this here
    } catch (err) {
      setValidationResult('Error: ' + err.message);
      setValidationOpen(true); // <-- And here, for error case
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
        body: JSON.stringify({ 
          apiKey, 
          outline, 
          sceneScript: scenes[1] 
        })
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

  const handleScene2Validate = async () => {
    setScene2VectorLoading(true);
    setScene2VectorInfo(null);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/scene-1-vector-info`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          apiKey, 
          outline, 
          sceneScript: scenes[2] 
        })
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setScene2VectorInfo(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setScene2VectorLoading(false);
    }
  };

  const handleWritersRoom = async (sceneNumber) => {
    setWritersRoomLoading(true);
    setError('');
    try {
      // Use different endpoint for scene 1
      const endpoint = sceneNumber === 1 ? '/scene-1-writers-room' : `/scene-writers-room/${sceneNumber}`;
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          apiKey, 
          outline,
          current_scene_script: scenes[sceneNumber]  // Add current scene script
        })
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setWritersRoomResultsByScene(prev => ({ ...prev, [sceneNumber]: data }));
      setShowWritersRoom(prev => ({ ...prev, [sceneNumber]: true }));  // Set show state for specific scene
    } catch (err) {
      setError(err.message);
    } finally {
      setWritersRoomLoading(false);
    }
  };

  const handleWritersRoom2 = async () => {
    setWritersRoomLoading2(true);
    setWritersRoomResults2(null);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/scene-1-writers-room`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey, outline })
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setWritersRoomResults2(data);
      setShowWritersRoom2(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setWritersRoomLoading2(false);
    }
  };

  const handleVectorInfo = async (sceneNumber) => {
    setVectorLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/scene-vector-info/${sceneNumber}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          apiKey, 
          outline, 
          sceneScript: scenes[sceneNumber] 
        })
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setVectorInfoByScene(prev => ({ ...prev, [sceneNumber]: data }));
      setShowVectorInfo(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setVectorLoading(false);
    }
  };

  const handleNext = async () => {
    if (currentFlow === 'concept') {
      if (activeStep === 1) {
        // Generate concept and move to next step
        await generateConcept();
        setActiveStep(2);
      } else if (activeStep === 2) {
        // Generate outline and move to next step
        await generateOutline();
        setActiveStep(3);
      } else if (activeStep === conceptSteps.length - 1) {
        // Switch to scene flow and generate Scene 1
        setCurrentFlow('scenes');
        setActiveStep(0);
        await generateScene1();
      } else {
        setActiveStep(prev => prev + 1);
      }
    } else {
      // In scene flow, generate next scene
      const nextSceneNumber = activeStep + 2; // +2 because activeStep starts at 0 and we want scene 2
      await generateNextScene(nextSceneNumber);
    }
  };

  const handleBack = () => {
    if (currentFlow === 'scenes' && activeStep === 0) {
      // Go back to concept flow
      setCurrentFlow('concept');
      setActiveStep(conceptSteps.length - 1);
    } else {
      setActiveStep(prev => prev - 1);
    }
  };

  const handleKeywordChange = (category) => (event) => {
    setKeywords({
      ...keywords,
      [category]: event.target.value
    });
  };

  const handleDownloadPDF = (sceneNumber) => {
    const script = scenes[sceneNumber];
    if (!script) return;

    // Get sitcom title (parse from concept or use a state variable)
    let title = '';
    if (concept) {
      const match = concept.match(/Title:\s*"?([^"]+)"?/i);
      if (match) title = match[1].replace(/\s+/g, '_');
      else title = 'sitcom';
    } else {
      title = 'sitcom';
    }

    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text(`${title.replace(/_/g, ' ')} - Scene ${sceneNumber}`, 10, 20);
    doc.setFontSize(12);

    // Split script into lines for PDF
    const lines = doc.splitTextToSize(script, 180);
    doc.text(lines, 10, 35);

    doc.save(`${title}_scene${sceneNumber}.pdf`);
  };

  const handleDownloadFullScript = () => {
    let script = '';
    for (let i = 1; i <= 20; i++) {
      if (scenes[i]) {
        script += `Scene ${i}\n\n${scenes[i]}\n\n`;
      }
    }
    let title = '';
    if (concept) {
      const match = concept.match(/Title:\s*"?([^"\n]+)"?/i);
      if (match) title = match[1].replace(/\s+/g, '_');
      else title = 'sitcom';
    } else {
      title = 'sitcom';
    }
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text(`${title.replace(/_/g, ' ')} - Complete Script`, 10, 20);
    doc.setFontSize(12);
    const lines = doc.splitTextToSize(script, 180);
    doc.text(lines, 10, 35);
    doc.save(`${title}_complete_script.pdf`);
  };

  const renderStepContent = (step) => {
    if (currentFlow === 'concept') {
      switch (step) {
        case 0:
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
        case 1:
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
                  onChange={(e) => setKeywords(prev => ({ ...prev, [cat.key]: e.target.value }))}
                  margin="normal"
                  helperText={cat.prompt}
                  sx={{ mb: 2 }}
                />
              ))}
              {concept && (
                <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
                  <Typography variant="h6" gutterBottom>Generated Concept:</Typography>
                  <Typography sx={{ whiteSpace: 'pre-line' }}>{concept}</Typography>
                </Paper>
              )}
            </Box>
          );
        case 2:
          return (
            <Box>
              <Typography variant="h6" gutterBottom>
                Generated Concept
              </Typography>
              {concept && (
                <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
                  {(() => {
                    const { title, description } = parseSitcomConcept(concept || '');
                    return <>
                      {title && (
                        <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 1 }}>{title}</Typography>
                      )}
                      <Typography sx={{ whiteSpace: 'pre-line' }}>{description}</Typography>
                    </>;
                  })()}
                </Paper>
              )}
            </Box>
          );
        case 3:
          return (
            <Box>
              <Button 
                variant="contained" 
                onClick={validateOutline} 
                disabled={validationLoading || loading}
                sx={{ mb: 2 }}
              >
                {validationLoading ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
                Validate Outline
              </Button>
              {outline && (
                <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
                  <Typography variant="h6" gutterBottom>Generated Outline:</Typography>
                  {formatOutline(outline)}
                </Paper>
              )}
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
                  width: '80%',
                  maxWidth: 800,
                  bgcolor: 'background.paper',
                  boxShadow: 24,
                  p: 4,
                  borderRadius: 2,
                  maxHeight: '80vh',
                  overflow: 'auto'
                }}>
                  <Typography id="validation-modal-title" variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Outline Validation Results
                  </Typography>
                  {validationLoading ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 4 }}>
                      <CircularProgress sx={{ mr: 2 }} />
                      <Typography>Validating outline...</Typography>
                    </Box>
                  ) : (
                    <>
                      <Typography id="validation-modal-description" sx={{ 
                        whiteSpace: 'pre-line',
                        mb: 3,
                        p: 2,
                        bgcolor: '#f5f5f5',
                        borderRadius: 1
                      }}>
                        {validationResult}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                        <Button 
                          onClick={() => setValidationOpen(false)} 
                          variant="contained"
                          sx={{ minWidth: 100 }}
                        >
                          Close
                        </Button>
                      </Box>
                    </>
                  )}
                </Box>
              </Modal>
            </Box>
          );
        default:
          return null;
      }
    } else {
      // Scene flow
      const sceneNumber = step + 1;
      return (
        <Box>
          <Typography variant="h6" gutterBottom>
            Scene {sceneNumber}
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Button variant="outlined" onClick={() => setShowOutlineModal(true)}>
              Show Outline
            </Button>
            <Button variant="outlined" onClick={() => setShowConceptModal(true)}>
              Show Concept
            </Button>
          </Box>
          
          {/* Outline Modal */}
          <Modal
            open={showOutlineModal}
            onClose={() => setShowOutlineModal(false)}
            aria-labelledby="outline-modal-title"
          >
            <Box sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '80%',
              maxWidth: 800,
              bgcolor: 'background.paper',
              boxShadow: 24,
              p: 4,
              borderRadius: 2,
              maxHeight: '80vh',
              overflow: 'auto'
            }}>
              <Typography id="outline-modal-title" variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
                Episode Outline
              </Typography>
              <Box sx={{ mt: 2 }}>
                {formatOutline(outline)}
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                <Button 
                  onClick={() => setShowOutlineModal(false)} 
                  variant="contained"
                  sx={{ minWidth: 100 }}
                >
                  Close
                </Button>
              </Box>
            </Box>
          </Modal>

          {/* Concept Modal */}
          <Modal
            open={showConceptModal}
            onClose={() => setShowConceptModal(false)}
            aria-labelledby="concept-modal-title"
          >
            <Box sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '80%',
              maxWidth: 800,
              bgcolor: 'background.paper',
              boxShadow: 24,
              p: 4,
              borderRadius: 2,
              maxHeight: '80vh',
              overflow: 'auto'
            }}>
              <Typography id="concept-modal-title" variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
                Sitcom Concept
              </Typography>
              <Box sx={{ mt: 2 }}>
                {(() => {
                  const { title, description } = parseSitcomConcept(concept || '');
                  return (
                    <>
                      {title && (
                        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>{title}</Typography>
                      )}
                      <Typography sx={{ whiteSpace: 'pre-line' }}>{description}</Typography>
                    </>
                  );
                })()}
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                <Button 
                  onClick={() => setShowConceptModal(false)} 
                  variant="contained"
                  sx={{ minWidth: 100 }}
                >
                  Close
                </Button>
              </Box>
            </Box>
          </Modal>
          
          {sceneNumber === 1 ? (
            <>
              {scenes[1] && (
                <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
                  <Typography sx={{ whiteSpace: 'pre-line' }}>{scenes[1]}</Typography>
                  <Button
                    variant="outlined"
                    sx={{ mt: 2 }}
                    onClick={() => handleDownloadPDF(1)}
                  >
                    Download Scene 1
                  </Button>
                </Paper>
              )}
              {scenes[1] && (
                <Box sx={{ mt: 3, mb: 2 }}>
                  <Button
                    variant="contained"
                    color="success"
                    onClick={() => handleVectorInfo(1)}
                    disabled={vectorLoading}
                  >
                    {vectorLoading ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
                    View Scene Metadata
                  </Button>
                </Box>
              )}
              {showVectorInfo && vectorInfoByScene[1] && (
                <Paper elevation={2} sx={{ p: 2, mt: 2, background: '#f5f5f5' }}>
                  <Typography variant="h6" gutterBottom>Vector Info for Scene 1:</Typography>
                  <Typography><b>Summary:</b> {vectorInfoByScene[1].summary}</Typography>
                  <Typography><b>Characters:</b> {vectorInfoByScene[1].characters}</Typography>
                  <Typography><b>Location:</b> {vectorInfoByScene[1].location}</Typography>
                  <Typography><b>Recurring Joke:</b> {vectorInfoByScene[1].recurring_joke}</Typography>
                  <Typography><b>Emotional Tone:</b> {vectorInfoByScene[1].emotional_tone}</Typography>
                </Paper>
              )}
              {showVectorInfo && vectorInfoByScene[1] && (
                <Box sx={{ mt: 3, mb: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleWritersRoom(1)}
                    disabled={writersRoomLoading}
                  >
                    {writersRoomLoading ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
                    Open Writer's Room
                  </Button>
                </Box>
              )}
              {showWritersRoom[1] && writersRoomResultsByScene[1] && (
                <Paper elevation={2} sx={{ p: 3, mt: 3, background: '#e3f2fd' }}>
                  <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 2 }}>
                    Writer's Room Results for Scene 1
                  </Typography>
                  
                  <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                    <Typography variant="h6" sx={{ mb: 1 }}>Character Analysis</Typography>
                    <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      Consistency:&nbsp;
                      {writersRoomResultsByScene[1]?.character?.is_consistent
                        ? <CheckCircleIcon color="success" fontSize="small" />
                        : <CancelIcon color="error" fontSize="small" />}
                      &nbsp;{writersRoomResultsByScene[1]?.character?.is_consistent ? 'Consistent' : 'Inconsistent'}
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Explanation:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[1].character.explanation ? 
                          splitNumbered(writersRoomResultsByScene[1].character.explanation).map((item, i) => (
                            <li key={i}>{item}</li>
                          )) : <li>No explanation available</li>}
                      </ul>
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Recommendations:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[1].character.recommendations ? 
                          splitRecommendations(writersRoomResultsByScene[1].character.recommendations).map((rec, i) => (
                            <li key={i}>{rec}</li>
                          )) : <li>No recommendations available</li>}
                      </ul>
                    </Typography>
                  </Paper>

                  <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                    <Typography variant="h6" sx={{ mb: 1 }}>Comedic Analysis</Typography>
                    <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      Comedic Tone:&nbsp;
                      {writersRoomResultsByScene[1].comedic.is_consistent
                        ? <CheckCircleIcon color="success" fontSize="small" />
                        : <CancelIcon color="error" fontSize="small" />}
                      &nbsp;{writersRoomResultsByScene[1].comedic.is_consistent ? 'Consistent' : 'Inconsistent'}
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Analysis:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[1].comedic.analysis ? 
                          splitNumbered(writersRoomResultsByScene[1].comedic.analysis).map((item, i) => (
                            <li key={i}>{item}</li>
                          )) : <li>No analysis available</li>}
                      </ul>
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Recommendations:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[1].comedic.recommendations ? 
                          splitRecommendations(writersRoomResultsByScene[1].comedic.recommendations).map((rec, i) => (
                            <li key={i}>{rec}</li>
                          )) : <li>No recommendations available</li>}
                      </ul>
                    </Typography>
                  </Paper>

                  <Paper elevation={1} sx={{ p: 2 }}>
                    <Typography variant="h6" sx={{ mb: 1 }}>Environment Analysis</Typography>
                    <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      Consistency:&nbsp;
                      {writersRoomResultsByScene[1]?.environment?.is_consistent
                        ? <CheckCircleIcon color="success" fontSize="small" />
                        : <CancelIcon color="error" fontSize="small" />}
                      &nbsp;{writersRoomResultsByScene[1]?.environment?.is_consistent ? 'Consistent' : 'Inconsistent'}
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Transition:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[1]?.environment?.explanation ? 
                          splitByDash(writersRoomResultsByScene[1]?.environment?.explanation || '').map((item, i) => (
                            <li key={i}>{item}</li>
                          )) : <li>No transition analysis available</li>}
                      </ul>
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Suggestions:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[1]?.environment?.details_suggestions ? 
                          splitRecommendations(writersRoomResultsByScene[1]?.environment?.details_suggestions || '').map((rec, i) => (
                            <li key={i}>{rec}</li>
                          )) : <li>No suggestions available</li>}
                      </ul>
                    </Typography>
                  </Paper>
                </Paper>
              )}
            </>
          ) : (
            <>
              {scenes[sceneNumber] && (
                <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
                  <Typography sx={{ whiteSpace: 'pre-line' }}>{scenes[sceneNumber]}</Typography>
                  <Button
                    variant="outlined"
                    sx={{ mt: 2 }}
                    onClick={() => handleDownloadPDF(sceneNumber)}
                  >
                    Download Scene {sceneNumber}
                  </Button>
                </Paper>
              )}
              {scenes[sceneNumber] && (
                <Box sx={{ mt: 3, mb: 2 }}>
                  <Button
                    variant="contained"
                    color="success"
                    onClick={() => handleVectorInfo(sceneNumber)}
                    disabled={vectorLoading}
                  >
                    {vectorLoading ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
                    View Scene Metadata
                  </Button>
                </Box>
              )}
              {showVectorInfo && vectorInfoByScene[sceneNumber] && (
                <Paper elevation={2} sx={{ p: 2, mt: 2, background: '#f5f5f5' }}>
                  <Typography variant="h6" gutterBottom>Vector Info for Scene {sceneNumber}:</Typography>
                  <Typography><b>Summary:</b> {vectorInfoByScene[sceneNumber].summary}</Typography>
                  <Typography><b>Characters:</b> {vectorInfoByScene[sceneNumber].characters}</Typography>
                  <Typography><b>Location:</b> {vectorInfoByScene[sceneNumber].location}</Typography>
                  <Typography><b>Recurring Joke:</b> {vectorInfoByScene[sceneNumber].recurring_joke}</Typography>
                  <Typography><b>Emotional Tone:</b> {vectorInfoByScene[sceneNumber].emotional_tone}</Typography>
                </Paper>
              )}
              {showVectorInfo && vectorInfoByScene[sceneNumber] && (
                <Box sx={{ mt: 3, mb: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleWritersRoom(sceneNumber)}
                    disabled={writersRoomLoading}
                  >
                    {writersRoomLoading ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
                    Open Writer's Room
                  </Button>
                </Box>
              )}
              {showWritersRoom[sceneNumber] && writersRoomResultsByScene[sceneNumber] && (
                <Paper elevation={2} sx={{ p: 3, mt: 3, background: '#e3f2fd' }}>
                  <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 2 }}>
                    Writer's Room Results for Scene {sceneNumber}
                  </Typography>
                  
                  <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                    <Typography variant="h6" sx={{ mb: 1 }}>Character Analysis</Typography>
                    <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      Consistency:&nbsp;
                      {writersRoomResultsByScene[sceneNumber]?.character?.is_consistent
                        ? <CheckCircleIcon color="success" fontSize="small" />
                        : <CancelIcon color="error" fontSize="small" />}
                      &nbsp;{writersRoomResultsByScene[sceneNumber]?.character?.is_consistent ? 'Consistent' : 'Inconsistent'}
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Explanation:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[sceneNumber].character.explanation ? 
                          splitNumbered(writersRoomResultsByScene[sceneNumber].character.explanation).map((item, i) => (
                            <li key={i}>{item}</li>
                          )) : <li>No explanation available</li>}
                      </ul>
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Recommendations:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[sceneNumber].character.recommendations ? 
                          splitRecommendations(writersRoomResultsByScene[sceneNumber].character.recommendations).map((rec, i) => (
                            <li key={i}>{rec}</li>
                          )) : <li>No recommendations available</li>}
                      </ul>
                    </Typography>
                  </Paper>

                  <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                    <Typography variant="h6" sx={{ mb: 1 }}>Comedic Analysis</Typography>
                    <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      Comedic Tone:&nbsp;
                      {writersRoomResultsByScene[sceneNumber].comedic.is_consistent
                        ? <CheckCircleIcon color="success" fontSize="small" />
                        : <CancelIcon color="error" fontSize="small" />}
                      &nbsp;{writersRoomResultsByScene[sceneNumber].comedic.is_consistent ? 'Consistent' : 'Inconsistent'}
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Analysis:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[sceneNumber].comedic.analysis ? 
                          splitNumbered(writersRoomResultsByScene[sceneNumber].comedic.analysis).map((item, i) => (
                            <li key={i}>{item}</li>
                          )) : <li>No analysis available</li>}
                      </ul>
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Recommendations:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[sceneNumber].comedic.recommendations ? 
                          splitRecommendations(writersRoomResultsByScene[sceneNumber].comedic.recommendations).map((rec, i) => (
                            <li key={i}>{rec}</li>
                          )) : <li>No recommendations available</li>}
                      </ul>
                    </Typography>
                  </Paper>

                  <Paper elevation={1} sx={{ p: 2 }}>
                    <Typography variant="h6" sx={{ mb: 1 }}>Environment Analysis</Typography>
                    <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      Consistency:&nbsp;
                      {writersRoomResultsByScene[sceneNumber]?.environment?.is_consistent
                        ? <CheckCircleIcon color="success" fontSize="small" />
                        : <CancelIcon color="error" fontSize="small" />}
                      &nbsp;{writersRoomResultsByScene[sceneNumber]?.environment?.is_consistent ? 'Consistent' : 'Inconsistent'}
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Transition:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[sceneNumber]?.environment?.explanation ? 
                          splitByDash(writersRoomResultsByScene[sceneNumber]?.environment?.explanation || '').map((item, i) => (
                            <li key={i}>{item}</li>
                          )) : <li>No transition analysis available</li>}
                      </ul>
                    </Typography>
                    <Typography sx={{ mb: 1 }}>
                      <b>Suggestions:</b>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {writersRoomResultsByScene[sceneNumber]?.environment?.details_suggestions ? 
                          splitRecommendations(writersRoomResultsByScene[sceneNumber]?.environment?.details_suggestions || '').map((rec, i) => (
                            <li key={i}>{rec}</li>
                          )) : <li>No suggestions available</li>}
                      </ul>
                    </Typography>
                  </Paper>
                </Paper>
              )}
              {sceneNumber === 20 && (
                <Box sx={{ mt: 3, mb: 2 }}>
                  <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleDownloadFullScript}
                  >
                    Download Complete Script
                  </Button>
                </Box>
              )}
            </>
          )}
        </Box>
      );
    }
  };

  // Validation for keywords step
  const allKeywordsFilled = categories.every(cat => keywords[cat.key].trim() !== '');

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Sitcom Generator
      </Typography>
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {currentFlow === 'concept' ? (
          conceptSteps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))
        ) : (
          <Box>
            {chunkArray(sceneSteps, 5).map((row, rowIdx) => (
              <Stepper
                key={rowIdx}
                activeStep={activeStep - rowIdx * 5 >= 0 && activeStep - rowIdx * 5 < 5 ? activeStep - rowIdx * 5 : -1}
                sx={{ mb: 1 }}
              >
                {row.map((label, idx) => {
                  const globalIdx = rowIdx * 5 + idx;
                  return (
                    <Step key={label}>
                      <StepLabel
                        onClick={() => {
                          if (scenes[globalIdx + 1]) setActiveStep(globalIdx);
                        }}
                        style={{
                          cursor: scenes[globalIdx + 1] ? 'pointer' : 'not-allowed',
                          color: scenes[globalIdx + 1] ? 'inherit' : '#ccc'
                        }}
                      >
                        {label}
                      </StepLabel>
                    </Step>
                  );
                })}
              </Stepper>
            ))}
          </Box>
        )}
      </Stepper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {renderStepContent(activeStep)}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          disabled={loading}
          onClick={handleBack}
        >
          Back
        </Button>
        <Button
          variant="contained"
          onClick={handleNext}
          disabled={loading}
        >
          {loading ? (
            <>
              <CircularProgress size={20} sx={{ mr: 1 }} />
              {currentFlow === 'concept' && activeStep === 1 ? 'Generating Concept...' : 
               currentFlow === 'concept' && activeStep === 2 ? 'Generating Outline...' : 
               currentFlow === 'concept' && activeStep === conceptSteps.length - 1 ? 'Start Scenes' : 
               currentFlow === 'scenes' ? 'Next Scene' : 'Next'}
            </>
          ) : (
            currentFlow === 'concept' && activeStep === 1 ? 'Generate Concept' : 
            currentFlow === 'concept' && activeStep === 2 ? 'Generate Outline' :
            currentFlow === 'concept' && activeStep === conceptSteps.length - 1 ? 'Start Scenes' : 
            currentFlow === 'scenes' ? 'Next Scene' : 'Next'
          )}
        </Button>
      </Box>
    </Container>
  );
}

export default App; 