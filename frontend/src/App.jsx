import React, { useState, useEffect } from 'react'
import { api } from './api'
import TaskList from './components/TaskList'
import Stats from './components/Stats'
import IngestEmail from './components/IngestEmail'
import Chat from './components/Chat'

function App() {
  const [activeTab, setActiveTab] = useState('tasks')
  const [tasks, setTasks] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    try {
      setLoading(true)
      const [tasksData, statsData] = await Promise.all([
        api.getTasks(),
        api.getStats()
      ])
      setTasks(tasksData)
      setStats(statsData)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleEmailIngested = (result) => {
    if (result.status === 'created') {
      fetchData()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Aluminix - Sales Inbox Task Router
          </h1>
          <p className="mt-2 text-gray-600">
            AI-powered email classification and task management
          </p>
        </header>

        <nav className="flex space-x-4 mb-8 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('tasks')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'tasks'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Tasks
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'stats'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Statistics
          </button>
          <button
            onClick={() => setActiveTab('ingest')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'ingest'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Ingest Email
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'chat'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Chat
          </button>
        </nav>

        {loading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Loading...</p>
          </div>
        ) : (
          <>
            {activeTab === 'tasks' && <TaskList tasks={tasks} onRefresh={fetchData} />}
            {activeTab === 'stats' && <Stats stats={stats} />}
            {activeTab === 'ingest' && <IngestEmail onIngested={handleEmailIngested} />}
            {activeTab === 'chat' && <Chat />}
          </>
        )}
      </div>
    </div>
  )
}

export default App
