import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import OpportunityModal from '../components/Opportunities/OpportunityModal';
import '../components/Contacts/ContactModal.css';

const BACKEND_API = 'http://localhost:5000';
const pipelineStages = [
  'Prospecting',
  'Qualification',
  'Needs Analysis',
  'Proposal',
  'Negotiation',
  'Closed Won',
  'Closed Lost'
];

const OpportunitiesPage = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [columns, setColumns] = useState({});
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [opportunityToEdit, setOpportunityToEdit] = useState(null);

  useEffect(() => {
    fetch(`${BACKEND_API}/api/opportunities`)
      .then(res => res.json())
      .then(data => {
        if (data.items) setOpportunities(data.items);
        else setOpportunities([]);
      });
  }, []);

  useEffect(() => {
    // Map opportunities into columns by status
    const cols = {};
    pipelineStages.forEach(stage => {
      cols[stage] = [];
    });
    opportunities.forEach(opp => {
      const stage = opp.status || 'Prospecting';
      if (!cols[stage]) cols[stage] = [];
      cols[stage].push(opp);
    });
    setColumns(cols);
  }, [opportunities]);

  const onDragEnd = async (result) => {
    const { source, destination, draggableId } = result;
    if (!destination) return;
    if (source.droppableId === destination.droppableId) return;
    const oppId = draggableId;
    const newStatus = destination.droppableId;
    // Update backend
    await fetch(`${BACKEND_API}/api/opportunities/${oppId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });
    // Refresh data
    fetch(`${BACKEND_API}/api/opportunities`)
      .then(res => res.json())
      .then(data => {
        if (data.items) setOpportunities(data.items);
        else setOpportunities([]);
      });
  };

  return (
    <div className="opportunities-page">
      <h1 className="page-title">Opportunities (Kanban Board)</h1>
      <button
        className="add-opportunity-btn"
        onClick={() => {
          setIsModalOpen(true);
          setOpportunityToEdit(null);
        }}
        style={{ marginBottom: '1rem' }}
      >
        Add Opportunity
      </button>
      <div className="kanban-board" style={{ display: 'flex', gap: '1rem', overflowX: 'auto' }}>
        <DragDropContext onDragEnd={onDragEnd}>
          {pipelineStages.map(stage => (
            <Droppable droppableId={stage} key={stage}>
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className="kanban-column"
                  style={{ minWidth: 250, background: '#f4f4f4', borderRadius: 8, padding: 8 }}
                >
                  <h2 style={{ textAlign: 'center' }}>{stage}</h2>
                  {columns[stage] && columns[stage].map((opp, idx) => (
                    <Draggable draggableId={String(opp.id)} index={idx} key={opp.id}>
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className="kanban-card"
                          style={{
                            userSelect: 'none',
                            margin: '0 0 8px 0',
                            padding: 16,
                            background: '#fff',
                            borderRadius: 6,
                            boxShadow: '0 2px 6px rgba(0,0,0,0.07)',
                            ...provided.draggableProps.style
                          }}
                        >
                          <div><strong>{opp.name}</strong></div>
                          <div>Account: {opp.account_name}</div>
                          <div>Value: R {opp.value}</div>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          ))}
        </DragDropContext>
      </div>
      <OpportunityModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        opportunityToEdit={opportunityToEdit}
        onSave={() => {
          fetch(`${BACKEND_API}/api/opportunities`)
            .then(res => res.json())
            .then(data => {
              if (data.items) setOpportunities(data.items);
              else setOpportunities([]);
            });
        }}
      />
    </div>
  );
};

export default OpportunitiesPage;