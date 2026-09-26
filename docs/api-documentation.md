# Inteliedu - REST & Real-time API Documentation

## 1. Overview & Base Configuration
- **Base URL**: `http://localhost:5000/api/v1` (Development) / `https://api.inteliedu.com/api/v1` (Production)
- **Protocol**: HTTPS / WSS
- **Standard Response Envelope**:
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "errors": null
}
```

---

## 2. API Route Specifications

### 2.1 Authentication (`/auth`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/signup` | Register new user account with role | No |
| `POST` | `/auth/login` | Authenticate user & return JWT token | No |
| `POST` | `/auth/logout` | Invalidate current session | Yes |
| `POST` | `/auth/refresh` | Refresh access token | Yes |
| `POST` | `/auth/forgot-password` | Send password reset email | No |
| `POST` | `/auth/reset-password` | Update password with reset token | No |

### 2.2 Users & Profiles (`/users`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/users/me` | Fetch authenticated user profile & role | Yes |
| `PATCH` | `/users/me` | Update personal profile details | Yes |
| `GET` | `/users` | List platform users (filtered by role/class) | Admin / Teacher |
| `GET` | `/users/:id` | Fetch specific user details | Admin / Teacher |
| `DELETE` | `/users/:id` | Deactivate/remove user account | Admin |

### 2.3 Classes (`/classes`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/classes` | List classes for authenticated user | Yes |
| `POST` | `/classes` | Create a new classroom | Teacher / Admin |
| `GET` | `/classes/:id` | Get class details, schedule, and roster | Yes |
| `PATCH` | `/classes/:id` | Update class metadata | Teacher / Admin |
| `DELETE` | `/classes/:id` | Archive or delete class | Teacher / Admin |
| `POST` | `/classes/join` | Join class via invitation code | Student |
| `GET` | `/classes/:id/members` | Get enrolled students | Yes |

### 2.4 Courses (`/courses`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/courses` | List courses by class or subject | Yes |
| `POST` | `/courses` | Create new course curriculum | Teacher / Admin |
| `GET` | `/courses/:id` | Get course details and lesson outline | Yes |
| `PATCH` | `/courses/:id` | Update course details | Teacher / Admin |
| `DELETE` | `/courses/:id` | Delete course | Teacher / Admin |

### 2.5 Lessons (`/lessons`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/lessons/:id` | Retrieve lesson content, materials, and 3D links | Yes |
| `POST` | `/lessons` | Create new lesson within a course | Teacher / Admin |
| `PATCH` | `/lessons/:id` | Update lesson content or order | Teacher / Admin |
| `DELETE` | `/lessons/:id` | Delete lesson | Teacher / Admin |
| `POST` | `/lessons/:id/progress` | Update student progress / completion status | Student |

### 2.6 Learning Materials (`/materials`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/materials/lesson/:lessonId` | List materials attached to a lesson | Yes |
| `POST` | `/materials/upload` | Upload document to storage & trigger RAG vector indexing | Teacher / Admin |
| `GET` | `/materials/:id` | Get material metadata & download link | Yes |
| `DELETE` | `/materials/:id` | Delete material and remove associated embeddings | Teacher / Admin |

### 2.7 3D Models (`/three-d-models`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/three-d-models` | List available 3D models catalog | Yes |
| `GET` | `/three-d-models/:id` | Get 3D model metadata, annotations, GLB URL | Yes |
| `POST` | `/three-d-models` | Register new 3D model asset | Admin / Teacher |
| `PATCH` | `/three-d-models/:id/annotations` | Update interactive pins/annotations | Teacher / Admin |

### 2.8 AI Tutor (`/ai`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/ai/chat` | Send message to AI Tutor (RAG context-injected) | Yes |
| `GET` | `/ai/conversations` | Retrieve student's conversation history | Yes |
| `GET` | `/ai/conversations/:id` | Get message history for specific conversation | Yes |
| `POST` | `/ai/generate-quiz` | Automatically generate quiz questions from lesson content | Teacher |
| `POST` | `/ai/summarize` | Generate simplified summary of lesson notes | Yes |
| `POST` | `/ai/voice-query` | Process audio speech stream and return audio answer | Yes |

### 2.9 Quizzes (`/quizzes`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/quizzes/lesson/:lessonId` | Get quizzes assigned to a lesson | Yes |
| `GET` | `/quizzes/:id` | Get quiz questions (without answers for students) | Yes |
| `POST` | `/quizzes` | Create a new quiz | Teacher / Admin |
| `POST` | `/quizzes/:id/submit` | Submit quiz answers for automated evaluation | Student |
| `GET` | `/quizzes/:id/attempts` | View student attempts and scores | Teacher / Admin |

### 2.10 Assignments (`/assignments`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/assignments/lesson/:lessonId` | List assignments for lesson | Yes |
| `POST` | `/assignments` | Publish new assignment with deadline | Teacher / Admin |
| `POST` | `/assignments/:id/submit` | Submit student coursework | Student |
| `GET` | `/assignments/:id/submissions` | Get student submissions list | Teacher |
| `PATCH` | `/assignments/submissions/:id/grade` | Submit grade and feedback | Teacher |

### 2.11 Attendance (`/attendance`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/attendance/check-in` | Auto check-in student to live session | Student |
| `GET` | `/attendance/class/:classId` | Get attendance records for a class session | Teacher / Admin |
| `PATCH` | `/attendance/:id` | Manual override of student attendance status | Teacher / Admin |

### 2.12 Analytics (`/analytics`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/analytics/student/me` | Fetch personal learning metrics & mastery stats | Student |
| `GET` | `/analytics/student/:id` | Fetch specific student performance report | Teacher / Admin |
| `GET` | `/analytics/class/:classId` | Aggregated class performance & quiz metrics | Teacher / Admin |
| `GET` | `/analytics/system` | Platform-wide user engagement & storage metrics | Admin |
