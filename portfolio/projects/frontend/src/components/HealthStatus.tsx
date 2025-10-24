import React from 'react';
import { HealthResponse } from '../api/client';

type Props = {
  health: HealthResponse | null;
  isLoading: boolean;
};

const HealthStatus: React.FC<Props> = ({ health, isLoading }) => {
  if (isLoading) {
    return <p className="status status--loading">Checking service health…</p>;
  }

  if (!health) {
    return <p className="status status--error">Service health unavailable.</p>;
  }

  return (
    <p className="status status--ok">
      Backend status: <strong>{health.status}</strong> ({health.environment})
    </p>
  );
};

export default HealthStatus;
