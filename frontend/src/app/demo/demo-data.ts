// Fixture exclusivamente visual. No representa una malla ni un período institucional.
export type Priority = 'Alta' | 'Media' | 'Baja';
export interface DemoCourse {
  id: string;
  name: string;
  level: number;
  credits: number;
  state: 'Aprobada' | 'Reprobada' | 'No cursada' | null;
  available: boolean;
  reason: string;
  high: number;
  medium: number;
  low: number;
}
export const DEMO_COURSES: readonly DemoCourse[] = [
  {
    id: 'DEMO101',
    name: 'FUNDAMENTOS DE PROGRAMACIÓN',
    level: 1,
    credits: 3,
    state: 'Aprobada',
    available: false,
    reason: 'Ya declarada aprobada',
    high: 4,
    medium: 2,
    low: 1,
  },
  {
    id: 'DEMO201',
    name: 'ESTRUCTURAS DE DATOS',
    level: 2,
    credits: 3,
    state: 'Reprobada',
    available: true,
    reason: 'DEMO101 declarado aprobado',
    high: 12,
    medium: 6,
    low: 3,
  },
  {
    id: 'DEMO202',
    name: 'MATEMÁTICA DISCRETA',
    level: 2,
    credits: 3,
    state: 'No cursada',
    available: true,
    reason: 'Sin prerrequisitos en este ejemplo',
    high: 9,
    medium: 5,
    low: 2,
  },
  {
    id: 'DEMO301',
    name: 'BASES DE DATOS',
    level: 3,
    credits: 3,
    state: 'No cursada',
    available: false,
    reason: 'Requiere DEMO201 aprobado; declarado reprobado',
    high: 8,
    medium: 4,
    low: 2,
  },
  {
    id: 'DEMO302',
    name: 'REDES',
    level: 3,
    credits: 3,
    state: null,
    available: false,
    reason: 'Falta declarar el estado de esta asignatura',
    high: 7,
    medium: 3,
    low: 1,
  },
  {
    id: 'DEMO203',
    name: 'COMUNICACIÓN ACADÉMICA',
    level: 2,
    credits: 2,
    state: 'No cursada',
    available: true,
    reason: 'Sin prerrequisitos en este ejemplo',
    high: 3,
    medium: 4,
    low: 2,
  },
  {
    id: 'DEMO204',
    name: 'ESTADÍSTICA',
    level: 2,
    credits: 3,
    state: 'No cursada',
    available: true,
    reason: 'Sin prerrequisitos en este ejemplo',
    high: 6,
    medium: 5,
    low: 3,
  },
  {
    id: 'DEMO205',
    name: 'TALLER DE INVESTIGACIÓN',
    level: 2,
    credits: 2,
    state: 'No cursada',
    available: true,
    reason: 'Sin prerrequisitos en este ejemplo',
    high: 2,
    medium: 3,
    low: 4,
  },
];
