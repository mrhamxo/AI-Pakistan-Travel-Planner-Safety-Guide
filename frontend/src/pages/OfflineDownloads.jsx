import React from 'react'
import { Download, MapPin, Mountain, Building } from 'lucide-react'
import './OfflineDownloads.css'

function OfflineDownloads() {
  const cityPacks = [
    {
      name: 'Islamabad & Rawalpindi',
      size: '2.5 MB',
      includes: ['Route maps', 'Transport schedules', 'Safety tips', 'Emergency contacts']
    },
    {
      name: 'Karachi',
      size: '3.1 MB',
      includes: ['Route maps', 'Transport schedules', 'Safety tips', 'Emergency contacts']
    },
    {
      name: 'Lahore',
      size: '2.8 MB',
      includes: ['Route maps', 'Transport schedules', 'Safety tips', 'Emergency contacts']
    },
  ]

  const northernPacks = [
    {
      name: 'Gilgit-Baltistan',
      size: '5.2 MB',
      includes: [
        'Offline route maps',
        'Altitude warnings',
        'Weather patterns',
        'Packing checklist',
        'Emergency contacts',
        'Fuel station locations'
      ]
    },
    {
      name: 'Swat Valley',
      size: '4.1 MB',
      includes: [
        'Offline route maps',
        'Weather patterns',
        'Safety tips',
        'Emergency contacts',
        'Local transport info'
      ]
    },
    {
      name: 'Hunza Valley',
      size: '4.5 MB',
      includes: [
        'Offline route maps',
        'Altitude warnings',
        'Weather patterns',
        'Packing checklist',
        'Emergency contacts'
      ]
    },
  ]

  const handleDownload = (packName) => {
    // In a real implementation, this would download the pack
    alert(`Downloading ${packName} pack...\n\nNote: This is a demo. In production, this would download an offline data pack.`)
  }

  return (
    <div className="offline-downloads">
      <div className="downloads-header">
        <h1>Offline Travel Packs</h1>
        <p>Download travel information for offline use in low-connectivity areas</p>
      </div>

      <div className="downloads-info">
        <div className="info-card">
          <h3>📱 Why Download Offline Packs?</h3>
          <ul>
            <li>Access route information without internet</li>
            <li>Essential for northern areas with poor connectivity</li>
            <li>Includes safety tips and emergency contacts</li>
            <li>Maps and transport schedules pre-loaded</li>
          </ul>
        </div>
      </div>

      <div className="city-packs">
        <h2>
          <Building className="section-icon" />
          City Travel Packs
        </h2>
        <div className="packs-grid">
          {cityPacks.map((pack, idx) => (
            <div key={idx} className="pack-card">
              <h3>{pack.name}</h3>
              <div className="pack-size">{pack.size}</div>
              <div className="pack-includes">
                <strong>Includes:</strong>
                <ul>
                  {pack.includes.map((item, itemIdx) => (
                    <li key={itemIdx}>{item}</li>
                  ))}
                </ul>
              </div>
              <button 
                className="download-button"
                onClick={() => handleDownload(pack.name)}
              >
                <Download /> Download Pack
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="northern-packs">
        <h2>
          <Mountain className="section-icon" />
          Northern Areas Travel Packs
        </h2>
        <div className="packs-grid">
          {northernPacks.map((pack, idx) => (
            <div key={idx} className="pack-card northern">
              <h3>{pack.name}</h3>
              <div className="pack-size">{pack.size}</div>
              <div className="pack-includes">
                <strong>Includes:</strong>
                <ul>
                  {pack.includes.map((item, itemIdx) => (
                    <li key={itemIdx}>{item}</li>
                  ))}
                </ul>
              </div>
              <button 
                className="download-button"
                onClick={() => handleDownload(pack.name)}
              >
                <Download /> Download Pack
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="download-note">
        <p>
          <strong>Note:</strong> Offline packs are updated monthly. Download before your trip 
          to ensure you have the latest information. These packs work without internet connection 
          once downloaded.
        </p>
      </div>
    </div>
  )
}

export default OfflineDownloads
