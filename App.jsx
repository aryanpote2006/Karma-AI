import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Mic, Activity, Wind, Heart, 
  MapPin, Cloud, Upload, 
  Settings, BarChart3, CheckCircle, RefreshCw
} from 'lucide-react'
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, 
  CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts'
import toast, { Toaster } from 'react-hot-toast'

// Animation variants
const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
}

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

// AQI Categories
const aqiCategories = [
  { range: [0, 50], label: 'Good', color: '#00e400', description: 'Air quality is satisfactory' },
  { range: [51, 100], label: 'Moderate', color: '#ffff00', description: 'Acceptable' },
  { range: [101, 150], label: 'Unhealthy for Sensitive', color: '#ff7e00', description: 'Sensitive groups may experience effects' },
  { range: [151, 200], label: 'Unhealthy', color: '#ff0000', description: 'Everyone may experience effects' },
  { range: [201, 300], label: 'Very Unhealthy', color: '#8f3f97', description: 'Health alert' },
  { range: [301, 500], label: 'Hazardous', color: '#7e0023', description: 'Emergency conditions' }
]

const getAQICategory = (aqi) => {
  return aqiCategories.find(cat => aqi >= cat.range[0] && aqi <= cat.range[1]) || aqiCategories[5]
}

// Mock data for charts
const mockHistoricalData = [
  { time: '6AM', aqi: 45, pm25: 20, pm10: 35 },
  { time: '9AM', aqi: 78, pm25: 40, pm10: 65 },
  { time: '12PM', aqi: 120, pm25: 60, pm10: 85 },
  { time: '3PM', aqi: 95, pm25: 48, pm10: 72 },
  { time: '6PM', aqi: 85, pm25: 42, pm10: 68 },
  { time: '9PM', aqi: 65, pm25: 32, pm10: 55 },
]

const mockPredictionData = [
  { day: 'Today', aqi: 85 },
  { day: 'Tomorrow', aqi: 92 },
  { day: 'Day 3', aqi: 78 },
  { day: 'Day 4', aqi: 105 },
  { day: 'Day 5', aqi: 88 },
]

// Header Component
const Header = ({ activeTab, setActiveTab }) => (
  <motion.header initial={{ y: -100 }} animate={{ y: 0 }} className="glass-dark sticky top-0 z-50 px-6 py-4">
    <div className="max-w-7xl mx-auto flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
          <Wind className="w-7 h-7 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">AQI Assistant</h1>
          <p className="text-xs text-gray-400">AI-Powered Lung Health</p>
        </div>
      </div>
      
      <nav className="hidden md:flex items-center gap-2">
        {[
          { id: 'dashboard', label: 'Dashboard', icon: Activity },
          { id: 'predict', label: 'Predict', icon: Cloud },
          { id: 'voice', label: 'Voice', icon: Mic },
          { id: 'analytics', label: 'Analytics', icon: BarChart3 },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
              activeTab === tab.id ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </nav>

      <div className="flex items-center gap-3">
        <button className="p-2 rounded-lg bg-white/10 text-gray-400 hover:text-white transition-colors">
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </div>
  </motion.header>
)

// AQI Gauge Component
const AQIGauge = ({ value }) => {
  const category = getAQICategory(value)
  const percentage = Math.min((value / 500) * 100, 100)
  
  return (
    <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="relative w-64 h-64">
      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8" />
        <circle
          cx="50" cy="50" r="45"
          fill="none"
          stroke={category.color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={`${percentage * 2.83} 283`}
          className="transition-all duration-1000"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-5xl font-bold text-white">{value}</span>
        <span className="text-sm text-gray-400">AQI</span>
        <span className="mt-2 px-3 py-1 rounded-full text-xs font-semibold text-black" style={{ backgroundColor: category.color }}>
          {category.label}
        </span>
      </div>
    </motion.div>
  )
}

// Voice Assistant Component
const VoiceAssistant = ({ isListening, onToggleVoice, lastCommand, response }) => {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="show" className="glass-dark rounded-2xl p-6">
      <div className="flex flex-col items-center">
        <div className={`relative w-32 h-32 rounded-full flex items-center justify-center mb-6 ${isListening ? 'voice-pulse text-purple-500' : 'bg-white/10'}`}>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={onToggleVoice}
            className={`w-20 h-20 rounded-full flex items-center justify-center transition-colors ${
              isListening ? 'bg-red-500 text-white' : 'bg-purple-600 text-white hover:bg-purple-700'
            }`}
          >
            {isListening ? (
              <div className="audio-wave">
                {[...Array(5)].map((_, i) => (
                  <motion.span key={i} animate={{ height: [10, 40, 10] }} transition={{ repeat: Infinity, duration: 0.5, delay: i * 0.1 }} />
                ))}
              </div>
            ) : (
              <Mic className="w-8 h-8" />
            )}
          </motion.button>
        </div>

        <p className="text-lg text-gray-300 mb-4">{isListening ? 'Listening...' : 'Click to speak'}</p>

        {lastCommand && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
            <p className="text-sm text-gray-500 mb-1">You said:</p>
            <p className="text-white bg-white/5 rounded-lg px-4 py-2 mb-4">"{lastCommand}"</p>
          </motion.div>
        )}

        {response && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
            <p className="text-sm text-gray-500 mb-1">AI Response:</p>
            <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 rounded-lg px-4 py-3 border border-purple-500/30">
              <p className="text-white">{response}</p>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

// Prediction Form Component
const PredictionForm = ({ onPredict, isLoading }) => {
  const [formData, setFormData] = useState({
    city: '', pm25: '', pm10: '', no2: '', o3: '', so2: '', co: '', temperature: '', humidity: ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onPredict(formData)
  }

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  return (
    <motion.form variants={containerVariants} initial="hidden" animate="show" onSubmit={handleSubmit} className="glass-dark rounded-2xl p-6 space-y-6">
      <motion.div variants={itemVariants}>
        <label className="block text-sm text-gray-400 mb-2">City Name</label>
        <div className="relative">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input type="text" name="city" value={formData.city} onChange={handleChange} placeholder="Enter city name or pincode" className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-11 pr-4 text-white placeholder-gray-500" />
        </div>
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { name: 'pm25', label: 'PM2.5' },
          { name: 'pm10', label: 'PM10' },
          { name: 'no2', label: 'NO2' },
          { name: 'o3', label: 'O3' },
          { name: 'so2', label: 'SO2' },
          { name: 'co', label: 'CO' },
          { name: 'temperature', label: 'Temperature' },
          { name: 'humidity', label: 'Humidity' },
        ].map(field => (
          <div key={field.name}>
            <label className="block text-xs text-gray-500 mb-1">{field.label}</label>
            <input type="number" name={field.name} value={formData[field.name]} onChange={handleChange} placeholder="--" className="w-full bg-white/5 border border-white/10 rounded-lg py-2 px-3 text-white placeholder-gray-600 text-sm" />
          </div>
        ))}
      </motion.div>

      <motion.div variants={itemVariants}>
        <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} disabled={isLoading} type="submit" className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold py-4 rounded-xl flex items-center justify-center gap-2 disabled:opacity-50">
          {isLoading ? <><RefreshCw className="w-5 h-5 animate-spin" /> Analyzing...</> : <><Cloud className="w-5 h-5" /> Get AQI Prediction</>}
        </motion.button>
      </motion.div>
    </motion.form>
  )
}

// Result Card Component
const ResultCard = ({ prediction }) => {
  if (!prediction) return null
  const category = getAQICategory(prediction.aqi)

  return (
    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="glass-dark rounded-2xl p-6">
      <div className="flex flex-col md:flex-row gap-8 items-center">
        <AQIGauge value={prediction.aqi} />
        <div className="flex-1 space-y-4">
          <div className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-purple-400" />
            <span className="text-xl font-semibold text-white">{prediction.city || 'Unknown City'}</span>
          </div>
          <p className="text-gray-400">{category.description}</p>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Primary Pollutant</p>
              <p className="text-white font-semibold">PM2.5</p>
            </div>
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Confidence</p>
              <p className="text-white font-semibold">92%</p>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-6 pt-6 border-t border-white/10">
        <h4 className="text-sm font-semibold text-gray-400 mb-4">Pollutant Levels</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {Object.entries(prediction.pollutants || {}).map(([key, value]) => (
            <div key={key} className="flex justify-between items-center bg-white/5 rounded-lg px-3 py-2">
              <span className="text-gray-400 text-sm uppercase">{key}</span>
              <span className="text-white font-semibold">{value || '--'}</span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

// Lung Health Card Component
const LungHealthCard = ({ riskLevel, riskScore, recommendations }) => {
  const getRiskColor = (level) => {
    switch (level) {
      case 'Low': return '#00e400'
      case 'Moderate': return '#ffff00'
      case 'High': return '#ff7e00'
      case 'Critical': return '#ff0000'
      default: return '#888'
    }
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-dark rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-12 h-12 rounded-xl bg-red-600/20 flex items-center justify-center">
          <Heart className="w-6 h-6 text-red-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">Lung Health Risk</h3>
          <p className="text-sm text-gray-400">Based on current AQI exposure</p>
        </div>
      </div>
      <div className="flex items-center justify-center mb-6">
        <div className="relative w-32 h-32">
          <svg className="w-full h-full transform -rotate-90">
            <circle cx="64" cy="64" r="56" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="12" />
            <circle cx="64" cy="64" r="56" fill="none" stroke={getRiskColor(riskLevel)} strokeWidth="12" strokeLinecap="round" strokeDasharray={`${(riskScore / 100) * 352} 352`} />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold text-white">{riskScore}</span>
            <span className="text-xs text-gray-400">Risk Score</span>
          </div>
        </div>
      </div>
      <div className="text-center mb-4">
        <span className="px-4 py-1 rounded-full text-sm font-semibold" style={{ backgroundColor: getRiskColor(riskLevel), color: riskLevel === 'Low' ? '#000' : '#fff' }}>
          {riskLevel} Risk
        </span>
      </div>
      <div className="space-y-2">
        {recommendations?.map((rec, idx) => (
          <motion.div key={idx} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.1 }} className="flex items-start gap-3 bg-white/5 rounded-lg p-3">
            <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
            <p className="text-gray-300 text-sm">{rec}</p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

// Analytics Charts Component
const AnalyticsCharts = () => (
  <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-6">
    <motion.div variants={itemVariants} className="glass-dark rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4">24-Hour AQI Trend</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={mockHistoricalData}>
            <defs>
              <linearGradient id="aqiGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#667eea" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#667eea" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="time" stroke="#888" />
            <YAxis stroke="#888" />
            <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: 'none', borderRadius: '8px' }} />
            <Area type="monotone" dataKey="aqi" stroke="#667eea" fill="url(#aqiGradient)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>

    <motion.div variants={itemVariants} className="glass-dark rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Pollutant Levels</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={mockHistoricalData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="time" stroke="#888" />
            <YAxis stroke="#888" />
            <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: 'none', borderRadius: '8px' }} />
            <Bar dataKey="pm25" fill="#764ba2" radius={[4, 4, 0, 0]} />
            <Bar dataKey="pm10" fill="#667eea" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>

    <motion.div variants={itemVariants} className="glass-dark rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4">5-Day AQI Forecast</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={mockPredictionData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="day" stroke="#888" />
            <YAxis stroke="#888" />
            <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: 'none', borderRadius: '8px' }} />
            <Line type="monotone" dataKey="aqi" stroke="#00e400" strokeWidth={2} dot={{ fill: '#00e400' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  </motion.div>
)

// File Upload Component
const FileUpload = ({ onUpload, isUploading }) => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-dark rounded-2xl p-6">
    <div className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center">
      <Upload className="w-12 h-12 text-gray-500 mx-auto mb-4" />
      <p className="text-gray-400 mb-2">Upload CSV or JSON file with air quality data</p>
      <p className="text-sm text-gray-600 mb-4">Supported formats: .csv, .json</p>
      <input type="file" accept=".csv,.json" onChange={onUpload} disabled={isUploading} className="hidden" id="file-upload" />
      <label htmlFor="file-upload" className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg cursor-pointer hover:bg-purple-700 transition-colors">
        {isUploading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
        {isUploading ? 'Uploading...' : 'Choose File'}
      </label>
    </div>
  </motion.div>
)

// Dashboard Component
const Dashboard = ({ prediction, lungHealth }) => (
  <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-6">
    <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {[
        { icon: Wind, label: 'Current AQI', value: prediction?.aqi || '--' },
        { icon: Activity, label: 'Air Quality', value: prediction?.category || 'N/A' },
        { icon: Heart, label: 'Lung Risk', value: lungHealth?.riskLevel || 'N/A' },
        { icon: Cloud, label: 'Temperature', value: prediction?.meteorological?.temperature || '--', unit: 'C' },
      ].map((stat, idx) => (
        <div key={idx} className="glass-dark rounded-xl p-4">
          <div className="w-10 h-10 rounded-lg bg-purple-600/20 flex items-center justify-center mb-3">
            <stat.icon className="w-5 h-5 text-purple-400" />
          </div>
          <p className="text-sm text-gray-400">{stat.label}</p>
          <p className="text-xl font-bold text-white">{stat.value}{stat.unit || ''}</p>
        </div>
      ))}
    </motion.div>

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ResultCard prediction={prediction} />
      <LungHealthCard 
        riskLevel={lungHealth?.riskLevel || 'Low'}
        riskScore={lungHealth?.riskScore || 15}
        recommendations={lungHealth?.recommendations || ['Air quality is good. Enjoy outdoor activities!', 'No specific precautions needed.']}
      />
    </div>
  </motion.div>
)

// Main App
function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [isListening, setIsListening] = useState(false)
  const [lastCommand, setLastCommand] = useState('')
  const [aiResponse, setAiResponse] = useState('')
  const [prediction, setPrediction] = useState(null)
  const [lungHealth, setLungHealth] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  useEffect(() => {
    const demoPrediction = {
      aqi: 85, category: 'Moderate', city: 'Demo City',
      pollutants: { pm25: 42, pm10: 68, no2: 25, o3: 35, so2: 8, co: 0.5 },
      meteorological: { temperature: 28, humidity: 65 }
    }
    setPrediction(demoPrediction)
    setLungHealth({ riskLevel: 'Moderate', riskScore: 35, recommendations: ['Consider limiting prolonged outdoor exertion.', 'Sensitive individuals should monitor symptoms.'] })
  }, [])

  const handlePredict = async (data) => {
    setIsLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1500))
      const aqiValue = Math.floor(Math.random() * 150) + 50
      const mockPrediction = {
        aqi: aqiValue,
        category: getAQICategory(aqiValue).label,
        city: data.city || 'Unknown',
        pollutants: {
          pm25: data.pm25 || Math.floor(Math.random() * 50),
          pm10: data.pm10 || Math.floor(Math.random() * 80),
          no2: data.no2 || Math.floor(Math.random() * 40),
          o3: data.o3 || Math.floor(Math.random() * 60),
          so2: data.so2 || Math.floor(Math.random() * 20),
          co: data.co || (Math.random() * 1).toFixed(1)
        },
        meteorological: {
          temperature: data.temperature || Math.floor(Math.random() * 15) + 20,
          humidity: data.humidity || Math.floor(Math.random() * 30) + 50
        }
      }
      setPrediction(mockPrediction)
      const riskScore = Math.floor((mockPrediction.aqi / 500) * 100)
      setLungHealth({
        riskLevel: riskScore <= 20 ? 'Low' : riskScore <= 40 ? 'Moderate' : riskScore <= 60 ? 'High' : 'Critical',
        riskScore: riskScore,
        recommendations: riskScore <= 20 ? ['Air quality is good.', 'No precautions needed.'] : riskScore <= 40 ? ['Limit outdoor exertion.', 'Monitor symptoms.'] : riskScore <= 60 ? ['Reduce outdoor activities.', 'Wear mask.'] : ['Avoid outdoor activities.', 'Use air purifier.']
      })
      toast.success('Prediction complete!')
      setActiveTab('dashboard')
    } catch (error) {
      toast.error('Prediction failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleVoiceToggle = () => {
    if (isListening) {
      setIsListening(false)
      setLastCommand('Check AQI for Mumbai')
      setAiResponse('The current AQI in Mumbai is 85, which is in the Moderate range.')
    } else {
      setIsListening(true)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setIsUploading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 2000))
      toast.success('File processed successfully!')
      handlePredict({})
    } catch (error) {
      toast.error('File processing failed.')
    } finally {
      setIsUploading(false)
    }
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard': return <Dashboard prediction={prediction} lungHealth={lungHealth} />
      case 'predict': return (
        <div className="max-w-2xl mx-auto">
          <PredictionForm onPredict={handlePredict} isLoading={isLoading} />
          {prediction && <ResultCard prediction={prediction} />}
        </div>
      )
      case 'voice': return (
        <div className="max-w-2xl mx-auto">
          <VoiceAssistant isListening={isListening} onToggleVoice={handleVoiceToggle} lastCommand={lastCommand} response={aiResponse} />
          <div className="mt-6"><FileUpload onUpload={handleFileUpload} isUploading={isUploading} /></div>
        </div>
      )
      case 'analytics': return <AnalyticsCharts />
      default: return <Dashboard prediction={prediction} lungHealth={lungHealth} />
    }
  }

  return (
    <div className="min-h-screen">
      <Toaster position="top-right" />
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="max-w-7xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          <motion.div key={activeTab} variants={pageVariants} initial="initial" animate="animate" exit="exit" transition={{ duration: 0.3 }}>
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App
