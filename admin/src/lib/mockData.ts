// Comprehensive mock and live sync datasets for the ReVivo Admin Dashboard

export interface UserItem {
  id: number;
  name: string;
  email: string;
  role: 'customer' | 'technician' | 'admin';
  status: 'active' | 'suspended' | 'pending';
  deviceCount: number;
  totalSpent: number;
  joinedDate: string;
}

export interface TechnicianItem {
  id: number;
  name: string;
  businessName: string;
  email: string;
  serviceArea: string;
  rating: number;
  totalReviews: number;
  isVerified: boolean;
  status: 'active' | 'pending_verification' | 'suspended';
  skills: string[];
  activeRepairs: number;
  totalPayouts: number;
}

export interface DeviceItem {
  id: number;
  ownerName: string;
  ownerEmail: string;
  category: 'smartphone' | 'laptop';
  brand: string;
  model: string;
  condition: string;
  status: 'active' | 'repair' | 'repaired' | 'resold';
  hasPassport: boolean;
  registeredDate: string;
}

export interface RepairItem {
  id: number;
  code: string;
  customerName: string;
  device: string;
  technician: string;
  status: string;
  stageNumber: number;
  quoteAmount: number;
  isPaid: boolean;
  expectedTurnaround: string;
  createdAt: string;
}

export interface QuoteItem {
  id: number;
  repairCode: string;
  device: string;
  technician: string;
  version: number;
  isChangeRequest: boolean;
  laborCost: number;
  partsCost: number;
  otherFees: number;
  totalAmount: number;
  warranty: string;
  status: 'APPROVED' | 'PENDING' | 'REJECTED' | 'CLARIFICATION_REQUESTED' | 'SUPERSEDED';
  approvedAt?: string;
}

export interface PartItem {
  id: number;
  sku: string;
  name: string;
  partType: string;
  manufacturer: string;
  condition: 'OEM' | 'COMPATIBLE_THIRD_PARTY' | 'USED_TESTED';
  price: number;
  stock: number;
  warranty: string;
  seller: string;
  compatibleModels: string[];
}

export interface ResaleItem {
  id: number;
  code: string;
  customerName: string;
  device: string;
  conditionGrade: 'A' | 'B' | 'C';
  batteryHealth: number;
  originalPrice: number;
  valuationOffer: number;
  decisionRecommendation: 'SELL' | 'REPAIR' | 'REPLACE';
  status: 'SUBMITTED' | 'INSPECTION_PENDING' | 'OFFER_ACCEPTED' | 'PAID' | 'REJECTED';
  requestDate: string;
}

export interface OrderItem {
  id: number;
  orderNumber: string;
  supplier: string;
  technician: string;
  itemsCount: number;
  totalAmount: number;
  status: 'PROCESSING' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED';
  trackingNumber: string;
  orderDate: string;
}

export interface PaymentItem {
  id: number;
  transactionId: string;
  type: 'CUSTOMER_REPAIR' | 'TECHNICIAN_PAYOUT' | 'RESALE_BUYBACK' | 'PARTS_PURCHASE';
  amount: number;
  platformFee: number;
  payoutAmount: number;
  paymentMethod: 'Credit Card' | 'Apple Pay' | 'UPI' | 'Direct Bank Transfer';
  status: 'COMPLETED' | 'PENDING' | 'REFUNDED' | 'FAILED';
  date: string;
}

export interface WarrantyItem {
  id: number;
  passportId: string;
  device: string;
  customerName: string;
  provider: string;
  duration: string;
  startDate: string;
  expiryDate: string;
  daysRemaining: number;
  status: 'ACTIVE' | 'EXPIRED' | 'CLAIMED';
}

export interface ReviewItem {
  id: number;
  customerName: string;
  technicianName: string;
  repairCode: string;
  rating: number;
  comment: string;
  sentiment: 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE';
  date: string;
  status: 'PUBLISHED' | 'FLAGGED' | 'RESOLVED';
}

export interface DisputeItem {
  id: number;
  caseNumber: string;
  repairCode: string;
  customerName: string;
  technicianName: string;
  amount: number;
  issueReason: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'OPEN' | 'UNDER_REVIEW' | 'RESOLVED' | 'REFUNDED';
  createdAt: string;
}

export interface AuditLogItem {
  id: number;
  timestamp: string;
  adminUser: string;
  action: string;
  targetEntity: string;
  details: string;
  ipAddress: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
}

// ─── INITIAL SEED DATASETS ───────────────────────────────────────────────────

export const INITIAL_USERS: UserItem[] = [
  { id: 1, name: 'Alice Customer', email: 'alice@revivo.internal', role: 'customer', status: 'active', deviceCount: 3, totalSpent: 420.0, joinedDate: '2026-08-14' },
  { id: 2, name: 'Bob Fixer', email: 'bob.tech@revivo.internal', role: 'technician', status: 'active', deviceCount: 0, totalSpent: 0, joinedDate: '2026-07-22' },
  { id: 3, name: 'Carol Device Pro', email: 'carol@revivo.internal', role: 'customer', status: 'active', deviceCount: 2, totalSpent: 185.0, joinedDate: '2026-09-01' },
  { id: 4, name: 'David Smith', email: 'david@revivo.internal', role: 'technician', status: 'active', deviceCount: 0, totalSpent: 0, joinedDate: '2026-06-19' },
  { id: 5, name: 'Elena Rostova', email: 'elena@revivo.internal', role: 'customer', status: 'active', deviceCount: 1, totalSpent: 65.0, joinedDate: '2026-09-15' },
  { id: 6, name: 'Frank Miller', email: 'frank@revivo.internal', role: 'customer', status: 'suspended', deviceCount: 1, totalSpent: 0, joinedDate: '2026-09-20' },
  { id: 7, name: 'Master Administrator', email: 'admin@revivo.internal', role: 'admin', status: 'active', deviceCount: 0, totalSpent: 0, joinedDate: '2026-01-01' },
];

export const INITIAL_TECHNICIANS: TechnicianItem[] = [
  {
    id: 1,
    name: 'Bob Fixer',
    businessName: "Bob's Micro Repairs",
    email: 'bob.tech@revivo.internal',
    serviceArea: 'Austin, TX (Downtown & South)',
    rating: 4.9,
    totalReviews: 84,
    isVerified: true,
    status: 'active',
    skills: ['OLED Display Replacement', 'Logic Board Micro-Soldering', 'Battery Calibration'],
    activeRepairs: 6,
    totalPayouts: 14850.0,
  },
  {
    id: 2,
    name: 'Dave Tech',
    businessName: 'Apex Precision Repairs',
    email: 'dave.tech@revivo.internal',
    serviceArea: 'Seattle, WA (King County)',
    rating: 4.8,
    totalReviews: 62,
    isVerified: true,
    status: 'active',
    skills: ['MacBook Clamshell Displays', 'Dell Thermal Service', 'Cleanroom Camera Module Fix'],
    activeRepairs: 4,
    totalPayouts: 9200.0,
  },
  {
    id: 3,
    name: 'Vikram Sharma',
    businessName: 'Apex Circuit Labs',
    email: 'vikram.circuit@revivo.internal',
    serviceArea: 'San Francisco, CA',
    rating: 5.0,
    totalReviews: 19,
    isVerified: false,
    status: 'pending_verification',
    skills: ['SMD Component Rework', 'Water Damage Recovery', 'GPU Reballing'],
    activeRepairs: 1,
    totalPayouts: 1400.0,
  },
];

export const INITIAL_DEVICES: DeviceItem[] = [
  { id: 1, ownerName: 'Alice Customer', ownerEmail: 'alice@revivo.internal', category: 'smartphone', brand: 'Samsung', model: 'Galaxy S23', condition: 'Repaired & Inspected', status: 'repaired', hasPassport: true, registeredDate: '2026-08-14' },
  { id: 2, ownerName: 'Alice Customer', ownerEmail: 'alice@revivo.internal', category: 'laptop', brand: 'Dell', model: 'Inspiron 15', condition: 'Battery Serviced', status: 'active', hasPassport: true, registeredDate: '2026-08-15' },
  { id: 3, ownerName: 'Carol Device Pro', ownerEmail: 'carol@revivo.internal', category: 'smartphone', brand: 'Google', model: 'Pixel 7 Pro', condition: 'Good', status: 'repair', hasPassport: true, registeredDate: '2026-09-01' },
  { id: 4, ownerName: 'Elena Rostova', ownerEmail: 'elena@revivo.internal', category: 'laptop', brand: 'Apple', model: 'MacBook Pro 14 M1', condition: 'Brand New', status: 'active', hasPassport: true, registeredDate: '2026-09-15' },
  { id: 5, ownerName: 'Frank Miller', ownerEmail: 'frank@revivo.internal', category: 'smartphone', brand: 'Apple', model: 'iPhone 14 Pro', condition: 'Cracked Glass', status: 'active', hasPassport: false, registeredDate: '2026-09-20' },
];

export const INITIAL_REPAIRS: RepairItem[] = [
  { id: 1, code: 'REP-0001', customerName: 'Alice Customer', device: 'Samsung Galaxy S23', technician: "Bob's Micro Repairs", status: 'CUSTOMER_APPROVED', stageNumber: 6, quoteAmount: 220.0, isPaid: true, expectedTurnaround: '2 business days', createdAt: '2026-10-01' },
  { id: 2, code: 'REP-0002', customerName: 'Carol Device Pro', device: 'Google Pixel 7 Pro', technician: 'Apex Precision Repairs', status: 'REPAIR_IN_PROGRESS', stageNumber: 8, quoteAmount: 185.0, isPaid: true, expectedTurnaround: '1 business day', createdAt: '2026-10-02' },
  { id: 3, code: 'REP-0003', customerName: 'Alice Customer', device: 'Dell Inspiron 15', technician: 'Apex Precision Repairs', status: 'DELIVERED', stageNumber: 11, quoteAmount: 60.0, isPaid: true, expectedTurnaround: 'Completed', createdAt: '2026-09-12' },
  { id: 4, code: 'REP-0004', customerName: 'Elena Rostova', device: 'MacBook Pro 14 M1', technician: "Bob's Micro Repairs", status: 'QUOTE_PENDING', stageNumber: 5, quoteAmount: 450.0, isPaid: false, expectedTurnaround: '3 business days', createdAt: '2026-10-03' },
];

export const INITIAL_QUOTES: QuoteItem[] = [
  { id: 1, repairCode: 'REP-0001', device: 'Samsung Galaxy S23', technician: "Bob's Micro Repairs", version: 1, isChangeRequest: false, laborCost: 65.0, partsCost: 140.0, otherFees: 15.0, totalAmount: 220.0, warranty: '180 days parts & labor', status: 'APPROVED', approvedAt: '2026-10-01 14:30' },
  { id: 2, repairCode: 'REP-0002', device: 'Google Pixel 7 Pro', technician: 'Apex Precision Repairs', version: 1, isChangeRequest: false, laborCost: 45.0, partsCost: 130.0, otherFees: 10.0, totalAmount: 185.0, warranty: '90 days parts & labor', status: 'APPROVED', approvedAt: '2026-10-02 11:15' },
  { id: 3, repairCode: 'REP-0004', device: 'MacBook Pro 14 M1', technician: "Bob's Micro Repairs", version: 1, isChangeRequest: false, laborCost: 100.0, partsCost: 330.0, otherFees: 20.0, totalAmount: 450.0, warranty: '1 year OEM warranty', status: 'PENDING' },
];

export const INITIAL_PARTS: PartItem[] = [
  { id: 1, sku: 'SKU-SAM-S23-DISP-OEM', name: 'Samsung Galaxy S23 Dynamic AMOLED 2X Display (OEM)', partType: 'Screen', manufacturer: 'Samsung Electronics', condition: 'OEM', price: 145.0, stock: 15, warranty: '180 days', seller: 'ReVivo Official Store', compatibleModels: ['Galaxy S23', 'SM-S911B'] },
  { id: 2, sku: 'SKU-SAM-S23-BAT-OEM', name: 'Samsung Galaxy S23 3900mAh Li-ion Battery (OEM)', partType: 'Battery', manufacturer: 'Samsung Electronics', condition: 'OEM', price: 48.0, stock: 28, warranty: '1 year', seller: 'ReVivo Official Store', compatibleModels: ['Galaxy S23'] },
  { id: 3, sku: 'SKU-GOOG-P7P-DISP-OEM', name: 'Google Pixel 7 Pro 120Hz LTPO OLED Screen (OEM)', partType: 'Screen', manufacturer: 'Google Original', condition: 'OEM', price: 160.0, stock: 10, warranty: '180 days', seller: 'ReVivo Official Store', compatibleModels: ['Pixel 7 Pro'] },
  { id: 4, sku: 'SKU-APP-IP14P-BAT-TP', name: 'iPhone 14 Pro High-Capacity Battery (Compatible Third-Party)', partType: 'Battery', manufacturer: 'iFixit / Amprius', condition: 'COMPATIBLE_THIRD_PARTY', price: 42.0, stock: 18, warranty: '180 days', seller: 'Apex Mobile Spares', compatibleModels: ['iPhone 14 Pro'] },
  { id: 5, sku: 'SKU-DELL-XPS13-KB-USED', name: 'Dell XPS 13 Backlit US Keyboard Assembly (Used Tested)', partType: 'Keyboard', manufacturer: 'Dell Original Pull', condition: 'USED_TESTED', price: 40.0, stock: 5, warranty: '90 days', seller: 'EcoParts Refurb', compatibleModels: ['XPS 13 9310', 'XPS 13 9300'] },
];

export const INITIAL_RESALE: ResaleItem[] = [
  { id: 1, code: 'RES-1001', customerName: 'David Smith', device: 'Samsung Galaxy S22 Ultra', conditionGrade: 'A', batteryHealth: 92, originalPrice: 1199.0, valuationOffer: 420.0, decisionRecommendation: 'SELL', status: 'OFFER_ACCEPTED', requestDate: '2026-09-28' },
  { id: 2, code: 'RES-1002', customerName: 'Carol Device Pro', device: 'MacBook Air M1 2020', conditionGrade: 'B', batteryHealth: 84, originalPrice: 999.0, valuationOffer: 460.0, decisionRecommendation: 'SELL', status: 'INSPECTION_PENDING', requestDate: '2026-10-02' },
  { id: 3, code: 'RES-1003', customerName: 'Elena Rostova', device: 'iPhone 12 Mini', conditionGrade: 'C', batteryHealth: 77, originalPrice: 699.0, valuationOffer: 180.0, decisionRecommendation: 'REPLACE', status: 'SUBMITTED', requestDate: '2026-10-03' },
];

export const INITIAL_ORDERS: OrderItem[] = [
  { id: 1, orderNumber: 'PO-8821', supplier: 'ReVivo Official Central Hub', technician: "Bob's Micro Repairs", itemsCount: 4, totalAmount: 580.0, status: 'DELIVERED', trackingNumber: 'FEDEX-992100812', orderDate: '2026-09-30' },
  { id: 2, orderNumber: 'PO-8822', supplier: 'Apex Mobile Spares', technician: 'Apex Precision Repairs', itemsCount: 2, totalAmount: 185.0, status: 'SHIPPED', trackingNumber: 'UPS-1Z99823412', orderDate: '2026-10-02' },
  { id: 3, orderNumber: 'PO-8823', supplier: 'Global Tech Spares', technician: 'Apex Circuit Labs', itemsCount: 1, totalAmount: 48.0, status: 'PROCESSING', trackingNumber: 'AWAITING-DISPATCH', orderDate: '2026-10-03' },
];

export const INITIAL_PAYMENTS: PaymentItem[] = [
  { id: 1, transactionId: 'TXN-998124', type: 'CUSTOMER_REPAIR', amount: 220.0, platformFee: 33.0, payoutAmount: 187.0, paymentMethod: 'Credit Card', status: 'COMPLETED', date: '2026-10-01' },
  { id: 2, transactionId: 'TXN-998125', type: 'CUSTOMER_REPAIR', amount: 185.0, platformFee: 27.75, payoutAmount: 157.25, paymentMethod: 'Apple Pay', status: 'COMPLETED', date: '2026-10-02' },
  { id: 3, transactionId: 'TXN-998126', type: 'RESALE_BUYBACK', amount: 420.0, platformFee: 0.0, payoutAmount: 420.0, paymentMethod: 'Direct Bank Transfer', status: 'COMPLETED', date: '2026-09-29' },
  { id: 4, transactionId: 'TXN-998127', type: 'TECHNICIAN_PAYOUT', amount: 1485.0, platformFee: 0.0, payoutAmount: 1485.0, paymentMethod: 'Direct Bank Transfer', status: 'COMPLETED', date: '2026-09-30' },
];

export const INITIAL_WARRANTIES: WarrantyItem[] = [
  { id: 1, passportId: 'REVIVO-DPP-00001', device: 'Samsung Galaxy S23', customerName: 'Alice Customer', provider: "Bob's Micro Repairs / ReVivo", duration: '180 days', startDate: '2026-10-01', expiryDate: '2027-03-30', daysRemaining: 178, status: 'ACTIVE' },
  { id: 2, passportId: 'REVIVO-DPP-00002', device: 'Dell Inspiron 15', customerName: 'Alice Customer', provider: 'Apex Precision Repairs', duration: '180 days', startDate: '2026-09-12', expiryDate: '2027-03-12', daysRemaining: 160, status: 'ACTIVE' },
  { id: 3, passportId: 'REVIVO-DPP-00003', device: 'Google Pixel 7 Pro', customerName: 'Carol Device Pro', provider: 'Apex Precision Repairs', duration: '90 days', startDate: '2026-10-02', expiryDate: '2027-01-02', daysRemaining: 91, status: 'ACTIVE' },
  { id: 4, passportId: 'REVIVO-DPP-00004', device: 'MacBook Pro 14 M1', customerName: 'Elena Rostova', provider: 'Apple Manufacturer Limited', duration: '365 days', startDate: '2026-09-15', expiryDate: '2027-09-15', daysRemaining: 347, status: 'ACTIVE' },
];

export const INITIAL_REVIEWS: ReviewItem[] = [
  { id: 1, customerName: 'Alice Customer', technicianName: "Bob's Micro Repairs", repairCode: 'REP-0001', rating: 5, comment: 'Phenomenal service! Replaced the cracked AMOLED with genuine Samsung panel. Looks brand new.', sentiment: 'POSITIVE', date: '2026-10-02', status: 'PUBLISHED' },
  { id: 2, customerName: 'Alice Customer', technicianName: 'Apex Precision Repairs', repairCode: 'REP-0003', rating: 5, comment: 'Quick battery swap on Dell Inspiron. Battery life is restored to 9 hours.', sentiment: 'POSITIVE', date: '2026-09-14', status: 'PUBLISHED' },
  { id: 3, customerName: 'David Smith', technicianName: 'Apex Precision Repairs', repairCode: 'REP-0002', rating: 4, comment: 'Great repair quality, turnaround took 1 extra day due to shipment delay but great communication.', sentiment: 'POSITIVE', date: '2026-10-03', status: 'PUBLISHED' },
];

export const INITIAL_DISPUTES: DisputeItem[] = [
  { id: 1, caseNumber: 'DISP-401', repairCode: 'REP-0092', customerName: 'Frank Miller', technicianName: "Bob's Micro Repairs", amount: 140.0, issueReason: 'Customer claims rear housing has tiny hairline scratch after repair.', priority: 'MEDIUM', status: 'UNDER_REVIEW', createdAt: '2026-10-01' },
  { id: 2, caseNumber: 'DISP-402', repairCode: 'REP-0081', customerName: 'Sarah Jenkins', technicianName: 'Apex Circuit Labs', amount: 85.0, issueReason: 'Charging port intermittent after 14 days. Requesting zero-cost warranty re-inspection.', priority: 'LOW', status: 'OPEN', createdAt: '2026-10-02' },
];

export const INITIAL_AUDIT_LOGS: AuditLogItem[] = [
  { id: 1, timestamp: '2026-10-03 16:45:10', adminUser: 'admin@revivo.internal', action: 'PRICE_CHANGE_REQUEST_APPROVED', targetEntity: 'REP-0001 Quote v2', details: 'Authorized supplemental parts increase after customer signed approval.', ipAddress: '10.168.213.92', severity: 'INFO' },
  { id: 2, timestamp: '2026-10-03 14:12:05', adminUser: 'admin@revivo.internal', action: 'TECHNICIAN_VERIFIED', targetEntity: 'Tech #2 (Dave Tech)', details: 'Approved background credentials and ESD cleanroom certification.', ipAddress: '10.168.213.92', severity: 'INFO' },
  { id: 3, timestamp: '2026-10-03 11:30:22', adminUser: 'system_daemon', action: 'DEVICE_PASSPORT_SEALED', targetEntity: 'DEV-SAM-0001-SECURE', details: 'Digital passport cryptographic hash anchored for device #1.', ipAddress: '127.0.0.1', severity: 'INFO' },
  { id: 4, timestamp: '2026-10-02 18:20:00', adminUser: 'admin@revivo.internal', action: 'SECURITY_ALERT_RESOLVED', targetEntity: 'User #6 (Frank Miller)', details: 'Account placed on temporary review pending dispute resolution.', ipAddress: '10.168.213.92', severity: 'WARNING' },
];
