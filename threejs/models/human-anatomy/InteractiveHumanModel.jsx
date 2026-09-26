import React from 'react';
import HumanTeacherModel from './HumanTeacherModel.jsx';

/**
 * InteractiveHumanModel Proxy wrapper
 * Forwards to the realistic 3D Human Teacher Model
 */
export default function InteractiveHumanModel(props) {
  return <HumanTeacherModel {...props} />;
}
