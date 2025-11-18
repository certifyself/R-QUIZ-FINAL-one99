# SocraQuest Design System Guidelines

## GRADIENT RESTRICTION RULE
**NEVER** use dark/saturated gradient combos (e.g., purple/pink, blue-500 to purple-600) on any UI element.
**NEVER** let gradients cover more than 20% of the viewport.
**NEVER** apply gradients to text-heavy content or reading areas.
**NEVER** use gradients on small UI elements (<100px width).
**NEVER** stack multiple gradient layers in the same viewport.

### ENFORCEMENT RULE
IF gradient area exceeds 20% of viewport OR impacts readability
THEN fallback to solid colors or simple, two-color gradients.

### ALLOWED GRADIENT USAGE
- Hero/landing sections (background only, ensure text readability)
- Section backgrounds (not content blocks)
- Large CTA buttons / major interactive elements (light/simple gradients only)
- Decorative overlays and accent visuals

---

## Design Philosophy

SocraQuest embodies **intellectual curiosity meets modern gamification**. The design balances:
- **Sophisticated Learning**: Clean, focused quiz interfaces that minimize cognitive load
- **Motivating Engagement**: Subtle animations, progress indicators, and achievement celebrations
- **Trustworthy Authority**: Professional color palette inspired by classical philosophy with modern execution
- **Mobile-First PWA**: Touch-optimized, thumb-friendly interactions with fast load times

### Brand Attributes
- **Sophisticated**: Not childish - appeals to adult learners and knowledge seekers
- **Motivating**: Celebrates progress without being overwhelming
- **Trustworthy**: Clear information hierarchy, honest feedback
- **Accessible**: WCAG AA compliant, readable in all lighting conditions

---

## Color System

### Primary Palette
```json
{
  "primary": {
    "deep-ocean": "#0A4D68",
    "teal-600": "#088395",
    "teal-500": "#05BFDB",
    "cyan-400": "#00D9FF"
  },
  "neutral": {
    "slate-950": "#0F1419",
    "slate-900": "#1A202C",
    "slate-800": "#2D3748",
    "slate-700": "#4A5568",
    "slate-600": "#718096",
    "slate-400": "#A0AEC0",
    "slate-300": "#CBD5E0",
    "slate-200": "#E2E8F0",
    "slate-100": "#F7FAFC",
    "white": "#FFFFFF"
  },
  "accent": {
    "amber-500": "#F59E0B",
    "amber-400": "#FBBF24",
    "emerald-500": "#10B981",
    "rose-500": "#F43F5E"
  }
}
```

### Semantic Colors
```json
{
  "success": "#10B981",
  "error": "#F43F5E",
  "warning": "#F59E0B",
  "info": "#05BFDB",
  "correct-answer": "#10B981",
  "incorrect-answer": "#F43F5E",
  "locked": "#718096",
  "completed": "#088395"
}
```

### Background System
```json
{
  "app-background": "#F7FAFC",
  "card-background": "#FFFFFF",
  "elevated-card": "#FFFFFF",
  "quiz-background": "#FFFFFF",
  "admin-background": "#F7FAFC",
  "modal-overlay": "rgba(15, 20, 25, 0.75)",
  "skeleton-base": "#E2E8F0",
  "skeleton-highlight": "#F7FAFC"
}
```

### Gradient Usage (Limited to 20% viewport max)
```css
/* Hero Section Only - Subtle diagonal gradient */
.hero-gradient {
  background: linear-gradient(135deg, #0A4D68 0%, #088395 50%, #05BFDB 100%);
}

/* Primary CTA Button - Light gradient */
.cta-gradient {
  background: linear-gradient(180deg, #05BFDB 0%, #088395 100%);
}

/* Success State - Subtle glow */
.success-glow {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
}
```

### Color Usage Priority
1. **White backgrounds** (#FFFFFF) for all cards, quiz interfaces, and content areas
2. **Slate-100** (#F7FAFC) for app background and secondary surfaces
3. **Teal-600** (#088395) for primary actions, active states, and brand elements
4. **Gradient** only for hero sections and primary CTAs (max 20% of viewport)
5. **Amber-500** for achievements, badges, and celebration moments
6. **Slate-700** for body text, **Slate-900** for headings

---

## Typography

### Font Families
```css
/* Primary Font - Clean, Modern, Professional */
--font-primary: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Secondary Font - Readability for body text */
--font-secondary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Monospace - Timers, Scores, Stats */
--font-mono: 'Azeret Mono', 'Roboto Mono', monospace;
```

### Font Loading
```html
<!-- Add to index.html -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=Azeret+Mono:wght@500;600;700&display=swap" rel="stylesheet">
```

### Type Scale
```css
/* Headings */
--text-h1: 2.5rem;      /* 40px - Page titles */
--text-h2: 2rem;        /* 32px - Section headers */
--text-h3: 1.5rem;      /* 24px - Card titles */
--text-h4: 1.25rem;     /* 20px - Subsections */

/* Body */
--text-lg: 1.125rem;    /* 18px - Large body, quiz questions */
--text-base: 1rem;      /* 16px - Default body */
--text-sm: 0.875rem;    /* 14px - Secondary text */
--text-xs: 0.75rem;     /* 12px - Captions, labels */

/* Special */
--text-timer: 2rem;     /* 32px - Countdown timer */
--text-score: 3rem;     /* 48px - Final score display */
```

### Responsive Typography
```css
/* Mobile (default) */
.heading-hero {
  font-size: 2rem;        /* 32px */
  line-height: 1.2;
}

.heading-section {
  font-size: 1.5rem;      /* 24px */
  line-height: 1.3;
}

.quiz-question {
  font-size: 1.125rem;    /* 18px */
  line-height: 1.5;
}

/* Tablet (≥768px) */
@media (min-width: 768px) {
  .heading-hero {
    font-size: 2.5rem;    /* 40px */
  }
  
  .heading-section {
    font-size: 2rem;      /* 32px */
  }
  
  .quiz-question {
    font-size: 1.25rem;   /* 20px */
  }
}

/* Desktop (≥1024px) */
@media (min-width: 1024px) {
  .heading-hero {
    font-size: 3rem;      /* 48px */
  }
}
```

### Font Weights
```css
--font-regular: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Text Styles
```css
/* Headings - Space Grotesk */
h1, h2, h3, h4 {
  font-family: var(--font-primary);
  font-weight: var(--font-bold);
  color: #1A202C;
  letter-spacing: -0.02em;
}

/* Body - Inter */
body, p, span {
  font-family: var(--font-secondary);
  font-weight: var(--font-regular);
  color: #4A5568;
  line-height: 1.6;
}

/* Quiz Questions - Space Grotesk Medium */
.quiz-question-text {
  font-family: var(--font-primary);
  font-weight: var(--font-medium);
  font-size: 1.125rem;
  color: #1A202C;
  line-height: 1.5;
}

/* Timer - Azeret Mono */
.timer-display {
  font-family: var(--font-mono);
  font-weight: var(--font-bold);
  font-size: 2rem;
  color: #088395;
  letter-spacing: 0.05em;
}

/* Scores - Azeret Mono */
.score-display {
  font-family: var(--font-mono);
  font-weight: var(--font-bold);
  font-size: 3rem;
  color: #0A4D68;
}
```

---

## Spacing System

### Base Unit: 4px
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
```

### Component Spacing
```css
/* Cards */
--card-padding-mobile: 1rem;      /* 16px */
--card-padding-desktop: 1.5rem;   /* 24px */
--card-gap: 1rem;                 /* 16px between cards */

/* Quiz Interface */
--quiz-padding: 1.5rem;           /* 24px */
--option-gap: 0.75rem;            /* 12px between options */
--question-margin-bottom: 1.5rem; /* 24px */

/* Sections */
--section-padding-y: 2rem;        /* 32px vertical */
--section-padding-x: 1rem;        /* 16px horizontal mobile */
--section-gap: 3rem;              /* 48px between sections */

/* Admin Panel */
--admin-sidebar-width: 16rem;     /* 256px */
--admin-content-padding: 2rem;    /* 32px */
```

---

## Component Styles

### Buttons

#### Primary Button (CTA)
```jsx
// Component: Button (shadcn/ui)
// Path: /app/frontend/src/components/ui/button.jsx

// Usage Example:
<Button 
  data-testid="start-quiz-button"
  className="btn-primary"
>
  Start Quiz
</Button>

// CSS:
.btn-primary {
  background: linear-gradient(180deg, #05BFDB 0%, #088395 100%);
  color: #FFFFFF;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 1rem;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(8, 131, 149, 0.25);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(8, 131, 149, 0.35);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(8, 131, 149, 0.25);
}

.btn-primary:focus-visible {
  outline: 3px solid #05BFDB;
  outline-offset: 2px;
}
```

#### Secondary Button
```jsx
<Button 
  data-testid="view-leaderboard-button"
  variant="outline"
  className="btn-secondary"
>
  View Leaderboard
</Button>

// CSS:
.btn-secondary {
  background: #FFFFFF;
  color: #088395;
  border: 2px solid #088395;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 1rem;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.btn-secondary:hover {
  background: #F7FAFC;
  color: #0A4D68;
  border-color: #0A4D68;
}
```

#### Ghost Button
```jsx
<Button 
  data-testid="skip-button"
  variant="ghost"
  className="btn-ghost"
>
  Skip
</Button>

// CSS:
.btn-ghost {
  background: transparent;
  color: #718096;
  border: none;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.btn-ghost:hover {
  background: #F7FAFC;
  color: #4A5568;
}
```

#### Icon Button
```jsx
<Button 
  data-testid="close-modal-button"
  variant="ghost"
  size="icon"
  className="btn-icon"
>
  <X className="h-5 w-5" />
</Button>

// CSS:
.btn-icon {
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.btn-icon:hover {
  background: #F7FAFC;
}
```

### Cards

#### Quiz Card
```jsx
// Component: Card (shadcn/ui)
// Path: /app/frontend/src/components/ui/card.jsx

<Card data-testid="quiz-card" className="quiz-card">
  <CardHeader>
    <CardTitle>Daily Quest #1</CardTitle>
    <CardDescription>Geography</CardDescription>
  </CardHeader>
  <CardContent>
    <div className="quiz-card-status">
      <Badge variant="success">Completed</Badge>
      <span className="quiz-card-score">8/10</span>
    </div>
  </CardContent>
</Card>

// CSS:
.quiz-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.quiz-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: #088395;
}

.quiz-card-locked {
  opacity: 0.6;
  cursor: not-allowed;
  position: relative;
}

.quiz-card-locked::after {
  content: '🔒';
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 1.5rem;
}

.quiz-card-completed {
  border-color: #10B981;
  background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%);
}
```

#### Leaderboard Card
```jsx
<Card data-testid="leaderboard-card" className="leaderboard-card">
  <CardContent className="leaderboard-row">
    <div className="leaderboard-rank">1</div>
    <Avatar className="leaderboard-avatar">
      <AvatarFallback>JD</AvatarFallback>
    </Avatar>
    <div className="leaderboard-info">
      <p className="leaderboard-name">John Doe</p>
      <p className="leaderboard-score">2,450 pts</p>
    </div>
  </CardContent>
</Card>

// CSS:
.leaderboard-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 0.5rem;
  transition: background-color 0.2s ease;
}

.leaderboard-card.current-user {
  background: linear-gradient(90deg, #F0F9FF 0%, #E0F2FE 100%);
  border: 2px solid #088395;
  box-shadow: 0 4px 12px rgba(8, 131, 149, 0.15);
}

.leaderboard-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.leaderboard-rank {
  font-family: 'Azeret Mono', monospace;
  font-weight: 700;
  font-size: 1.25rem;
  color: #0A4D68;
  min-width: 2rem;
  text-align: center;
}

.leaderboard-rank.top-3 {
  color: #F59E0B;
}
```

### Quiz Interface Components

#### Quiz Option Button
```jsx
<button 
  data-testid="quiz-option-a"
  className="quiz-option"
  onClick={handleOptionSelect}
>
  <span className="quiz-option-label">A</span>
  <span className="quiz-option-text">Athens</span>
</button>

// CSS:
.quiz-option {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: #FFFFFF;
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  color: #2D3748;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quiz-option:hover {
  border-color: #088395;
  background: #F7FAFC;
  transform: translateX(4px);
}

.quiz-option.selected {
  border-color: #088395;
  background: #E0F2FE;
}

.quiz-option.correct {
  border-color: #10B981;
  background: #D1FAE5;
  animation: correctPulse 0.5s ease;
}

.quiz-option.incorrect {
  border-color: #F43F5E;
  background: #FFE4E6;
  animation: incorrectShake 0.5s ease;
}

.quiz-option.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.quiz-option-label {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: #E2E8F0;
  border-radius: 8px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  color: #4A5568;
  flex-shrink: 0;
}

.quiz-option.selected .quiz-option-label {
  background: #088395;
  color: #FFFFFF;
}

.quiz-option.correct .quiz-option-label {
  background: #10B981;
  color: #FFFFFF;
}

.quiz-option.incorrect .quiz-option-label {
  background: #F43F5E;
  color: #FFFFFF;
}

@keyframes correctPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

@keyframes incorrectShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-8px); }
  75% { transform: translateX(8px); }
}
```

#### Timer Component
```jsx
<div data-testid="quiz-timer" className="timer-container">
  <div className="timer-circle">
    <svg className="timer-svg" viewBox="0 0 100 100">
      <circle 
        className="timer-track" 
        cx="50" 
        cy="50" 
        r="45"
      />
      <circle 
        className="timer-progress" 
        cx="50" 
        cy="50" 
        r="45"
        style={{ strokeDashoffset: progressOffset }}
      />
    </svg>
    <div className="timer-text">{timeRemaining}s</div>
  </div>
</div>

// CSS:
.timer-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

.timer-circle {
  position: relative;
  width: 120px;
  height: 120px;
}

.timer-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.timer-track {
  fill: none;
  stroke: #E2E8F0;
  stroke-width: 8;
}

.timer-progress {
  fill: none;
  stroke: #088395;
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 283;
  transition: stroke-dashoffset 1s linear, stroke 0.3s ease;
}

.timer-progress.warning {
  stroke: #F59E0B;
}

.timer-progress.danger {
  stroke: #F43F5E;
  animation: timerPulse 1s infinite;
}

.timer-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'Azeret Mono', monospace;
  font-weight: 700;
  font-size: 2rem;
  color: #0A4D68;
}

@keyframes timerPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
```

#### Progress Bar
```jsx
// Component: Progress (shadcn/ui)
// Path: /app/frontend/src/components/ui/progress.jsx

<div data-testid="quiz-progress" className="progress-container">
  <div className="progress-info">
    <span className="progress-label">Question 3 of 10</span>
    <span className="progress-percentage">30%</span>
  </div>
  <Progress value={30} className="quiz-progress-bar" />
</div>

// CSS:
.progress-container {
  width: 100%;
  margin-bottom: 1.5rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-family: 'Inter', sans-serif;
  font-size: 0.875rem;
  color: #718096;
}

.quiz-progress-bar {
  height: 8px;
  background: #E2E8F0;
  border-radius: 4px;
  overflow: hidden;
}

.quiz-progress-bar > div {
  background: linear-gradient(90deg, #05BFDB 0%, #088395 100%);
  transition: width 0.3s ease;
}
```

### Badges

```jsx
// Component: Badge (shadcn/ui)
// Path: /app/frontend/src/components/ui/badge.jsx

// Status Badges
<Badge data-testid="quiz-status-badge" variant="success">Completed</Badge>
<Badge data-testid="quiz-status-badge" variant="warning">In Progress</Badge>
<Badge data-testid="quiz-status-badge" variant="secondary">Locked</Badge>

// Achievement Badges
<Badge data-testid="achievement-badge" className="badge-achievement">
  🏆 Perfect Score
</Badge>

// CSS:
.badge-achievement {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: #FFFFFF;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.badge-success {
  background: #D1FAE5;
  color: #065F46;
  border: 1px solid #10B981;
}

.badge-warning {
  background: #FEF3C7;
  color: #92400E;
  border: 1px solid #F59E0B;
}

.badge-secondary {
  background: #F7FAFC;
  color: #718096;
  border: 1px solid #CBD5E0;
}
```

### Modals & Dialogs

```jsx
// Component: Dialog (shadcn/ui)
// Path: /app/frontend/src/components/ui/dialog.jsx

<Dialog>
  <DialogTrigger asChild>
    <Button data-testid="open-results-modal">View Results</Button>
  </DialogTrigger>
  <DialogContent data-testid="results-modal" className="results-modal">
    <DialogHeader>
      <DialogTitle>Quiz Complete!</DialogTitle>
      <DialogDescription>
        You scored 8 out of 10
      </DialogDescription>
    </DialogHeader>
    <div className="results-content">
      {/* Results content */}
    </div>
    <DialogFooter>
      <Button data-testid="close-results-button">Close</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>

// CSS:
.results-modal {
  max-width: 500px;
  border-radius: 20px;
  padding: 2rem;
  background: #FFFFFF;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.results-modal .dialog-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #0A4D68;
  text-align: center;
}

.results-content {
  padding: 1.5rem 0;
  text-align: center;
}
```

### Ad Placeholders

#### Banner Ad
```jsx
<div data-testid="banner-ad" className="ad-banner">
  <div className="ad-label">Advertisement</div>
  <div className="ad-content">
    {/* Ad content or placeholder */}
  </div>
</div>

// CSS:
.ad-banner {
  width: 100%;
  max-width: 728px;
  margin: 2rem auto;
  padding: 1rem;
  background: #F7FAFC;
  border: 1px dashed #CBD5E0;
  border-radius: 8px;
  text-align: center;
}

.ad-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.75rem;
  color: #A0AEC0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.ad-content {
  min-height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF;
  border-radius: 4px;
}
```

#### Rewarded Ad Gate
```jsx
<div data-testid="ad-gate-modal" className="ad-gate">
  <div className="ad-gate-content">
    <h3 className="ad-gate-title">Watch Ad to Continue</h3>
    <p className="ad-gate-description">
      Watch a short ad to unlock your next attempt
    </p>
    <div className="ad-gate-countdown">
      <div className="countdown-circle">
        <svg className="countdown-svg" viewBox="0 0 100 100">
          <circle className="countdown-track" cx="50" cy="50" r="45" />
          <circle className="countdown-progress" cx="50" cy="50" r="45" />
        </svg>
        <div className="countdown-text">{countdown}s</div>
      </div>
    </div>
    <Button 
      data-testid="skip-ad-button"
      disabled={countdown > 0}
      className="ad-gate-button"
    >
      {countdown > 0 ? `Wait ${countdown}s` : 'Continue'}
    </Button>
  </div>
</div>

// CSS:
.ad-gate {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 20, 25, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.ad-gate-content {
  background: #FFFFFF;
  border-radius: 20px;
  padding: 2rem;
  max-width: 400px;
  width: 100%;
  text-align: center;
}

.ad-gate-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1A202C;
  margin-bottom: 0.5rem;
}

.ad-gate-description {
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  color: #718096;
  margin-bottom: 2rem;
}

.ad-gate-countdown {
  margin-bottom: 2rem;
}

.countdown-circle {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto;
}

.countdown-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.countdown-track {
  fill: none;
  stroke: #E2E8F0;
  stroke-width: 8;
}

.countdown-progress {
  fill: none;
  stroke: #F59E0B;
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 283;
  transition: stroke-dashoffset 1s linear;
}

.countdown-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'Azeret Mono', monospace;
  font-weight: 700;
  font-size: 2rem;
  color: #F59E0B;
}

.ad-gate-button {
  width: 100%;
}
```

---

## Layout & Grid System

### Mobile-First Container
```css
.app-container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1rem;
}

@media (min-width: 768px) {
  .app-container {
    padding: 0 2rem;
  }
}

@media (min-width: 1024px) {
  .app-container {
    padding: 0 3rem;
  }
}
```

### Quiz Layout
```css
/* Mobile-first quiz container */
.quiz-container {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.quiz-body {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.quiz-question {
  margin-bottom: 1.5rem;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.quiz-footer {
  margin-top: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

### Daily Quest Grid
```css
/* Mobile: Single column */
.quest-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  padding: 1rem;
}

/* Tablet: 2 columns */
@media (min-width: 768px) {
  .quest-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}

/* Desktop: 3 columns */
@media (min-width: 1024px) {
  .quest-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
  }
}

/* Bonus quest - full width */
.quest-grid .bonus-quest {
  grid-column: 1 / -1;
}
```

### Leaderboard Layout
```css
.leaderboard-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

.leaderboard-tabs {
  margin-bottom: 1.5rem;
}

.leaderboard-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
```

### Admin Panel Layout
```css
/* Desktop-first admin layout */
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #F7FAFC;
}

.admin-sidebar {
  width: 16rem;
  background: #FFFFFF;
  border-right: 1px solid #E2E8F0;
  padding: 1.5rem;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
}

.admin-main {
  flex: 1;
  margin-left: 16rem;
  padding: 2rem;
}

.admin-header {
  background: #FFFFFF;
  border-bottom: 1px solid #E2E8F0;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  border-radius: 12px;
}

.admin-content {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* Mobile admin - hamburger menu */
@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 100;
  }
  
  .admin-sidebar.open {
    transform: translateX(0);
  }
  
  .admin-main {
    margin-left: 0;
  }
}
```

---

## Micro-Interactions & Animations

### Hover States
```css
/* Card hover */
.interactive-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.interactive-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

/* Button hover */
.btn-hover {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(8, 131, 149, 0.35);
}

/* Quiz option hover */
.quiz-option:hover {
  transform: translateX(4px);
  border-color: #088395;
}
```

### Loading States
```jsx
// Component: Skeleton (shadcn/ui)
// Path: /app/frontend/src/components/ui/skeleton.jsx

<div className="quiz-card-skeleton">
  <Skeleton className="h-6 w-32 mb-2" />
  <Skeleton className="h-4 w-24 mb-4" />
  <Skeleton className="h-20 w-full" />
</div>

// CSS:
.skeleton {
  background: linear-gradient(
    90deg,
    #E2E8F0 0%,
    #F7FAFC 50%,
    #E2E8F0 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### Success Animations
```css
/* Correct answer pulse */
@keyframes correctPulse {
  0%, 100% { 
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  50% { 
    transform: scale(1.02);
    box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
  }
}

.correct-answer {
  animation: correctPulse 0.5s ease;
}

/* Achievement unlock */
@keyframes achievementSlideIn {
  0% {
    transform: translateY(-100%);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.achievement-notification {
  animation: achievementSlideIn 0.5s ease;
}
```

### Error Animations
```css
/* Incorrect answer shake */
@keyframes incorrectShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-8px); }
  75% { transform: translateX(8px); }
}

.incorrect-answer {
  animation: incorrectShake 0.5s ease;
}
```

### Page Transitions
```css
/* Fade in on mount */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-enter {
  animation: fadeIn 0.3s ease;
}

/* Slide transitions */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.slide-enter {
  animation: slideInRight 0.3s ease;
}
```

---

## Accessibility

### Focus States
```css
/* Global focus style */
*:focus-visible {
  outline: 3px solid #05BFDB;
  outline-offset: 2px;
  border-radius: 4px;
}

/* Button focus */
button:focus-visible {
  outline: 3px solid #05BFDB;
  outline-offset: 2px;
}

/* Input focus */
input:focus-visible,
textarea:focus-visible,
select:focus-visible {
  outline: 3px solid #05BFDB;
  outline-offset: 0;
  border-color: #088395;
}
```

### Color Contrast
All text meets WCAG AA standards:
- Body text (#4A5568) on white (#FFFFFF): 7.5:1
- Headings (#1A202C) on white (#FFFFFF): 14:1
- Primary button text (#FFFFFF) on teal (#088395): 4.8:1
- Secondary text (#718096) on white (#FFFFFF): 5.2:1

### Screen Reader Support
```jsx
// Always include aria labels for interactive elements
<button 
  data-testid="submit-answer-button"
  aria-label="Submit your answer"
>
  Submit
</button>

// Use aria-live for dynamic content
<div 
  data-testid="timer-display"
  aria-live="polite" 
  aria-atomic="true"
>
  {timeRemaining} seconds remaining
</div>

// Mark current state
<div 
  data-testid="quiz-progress"
  role="progressbar" 
  aria-valuenow={currentQuestion} 
  aria-valuemin={1} 
  aria-valuemax={10}
>
  Question {currentQuestion} of 10
</div>
```

### Keyboard Navigation
```css
/* Skip to main content link */
.skip-to-main {
  position: absolute;
  top: -40px;
  left: 0;
  background: #088395;
  color: #FFFFFF;
  padding: 0.5rem 1rem;
  text-decoration: none;
  border-radius: 0 0 8px 0;
  z-index: 1000;
}

.skip-to-main:focus {
  top: 0;
}
```

---

## Image Assets

### Image URLs by Category

#### Hero Section
```json
{
  "hero_background": "https://images.unsplash.com/photo-1759178966917-56dc2f7a0ccf",
  "description": "Abstract teal and black wavy textured background - Use as hero section background with overlay"
}
```

#### User Avatars / Profile
```json
{
  "student_learning_1": "https://images.pexels.com/photos/7092344/pexels-photo-7092344.jpeg",
  "description": "Student learning in classroom - Use for profile placeholders or testimonials",
  
  "student_learning_2": "https://images.pexels.com/photos/7092338/pexels-photo-7092338.jpeg",
  "description": "Student thinking - Use for empty states or profile examples"
}
```

#### Achievement / Success
```json
{
  "trophy_gold": "https://images.unsplash.com/photo-1642104744809-14b986179927",
  "description": "Glass trophy - Use for achievement badges, leaderboard top 3",
  
  "medals_display": "https://images.unsplash.com/photo-1759688983882-cf2b54df1562",
  "description": "Medals and trophies - Use for achievements page, badge showcase",
  
  "medal_blue": "https://images.pexels.com/photos/6120397/pexels-photo-6120397.jpeg",
  "description": "Blue medal - Use for completion badges"
}
```

#### Decorative / Background
```json
{
  "geometric_pattern": "https://images.unsplash.com/photo-1759267190544-9869df768d8e",
  "description": "Teal and black geometric pattern - Use for section backgrounds, decorative elements",
  
  "abstract_confetti": "https://images.unsplash.com/photo-1754366126082-848ad07310bc",
  "description": "Pink confetti on turquoise - Use for celebration modals, success screens"
}
```

#### Empty States
```json
{
  "quiz_worksheet": "https://images.unsplash.com/photo-1560785496-321917f24016",
  "description": "Math worksheet - Use for empty quiz states, no questions available"
}
```

---

## Component Paths (shadcn/ui)

### Core Components
```
/app/frontend/src/components/ui/button.jsx
/app/frontend/src/components/ui/card.jsx
/app/frontend/src/components/ui/badge.jsx
/app/frontend/src/components/ui/avatar.jsx
/app/frontend/src/components/ui/progress.jsx
/app/frontend/src/components/ui/skeleton.jsx
```

### Form Components
```
/app/frontend/src/components/ui/input.jsx
/app/frontend/src/components/ui/label.jsx
/app/frontend/src/components/ui/textarea.jsx
/app/frontend/src/components/ui/select.jsx
/app/frontend/src/components/ui/checkbox.jsx
/app/frontend/src/components/ui/radio-group.jsx
/app/frontend/src/components/ui/switch.jsx
/app/frontend/src/components/ui/form.jsx
```

### Navigation Components
```
/app/frontend/src/components/ui/tabs.jsx
/app/frontend/src/components/ui/navigation-menu.jsx
/app/frontend/src/components/ui/breadcrumb.jsx
/app/frontend/src/components/ui/pagination.jsx
```

### Overlay Components
```
/app/frontend/src/components/ui/dialog.jsx
/app/frontend/src/components/ui/sheet.jsx
/app/frontend/src/components/ui/drawer.jsx
/app/frontend/src/components/ui/alert-dialog.jsx
/app/frontend/src/components/ui/popover.jsx
/app/frontend/src/components/ui/tooltip.jsx
/app/frontend/src/components/ui/hover-card.jsx
```

### Data Display
```
/app/frontend/src/components/ui/table.jsx
/app/frontend/src/components/ui/alert.jsx
/app/frontend/src/components/ui/separator.jsx
/app/frontend/src/components/ui/scroll-area.jsx
```

### Advanced Components
```
/app/frontend/src/components/ui/calendar.jsx
/app/frontend/src/components/ui/command.jsx
/app/frontend/src/components/ui/dropdown-menu.jsx
/app/frontend/src/components/ui/context-menu.jsx
/app/frontend/src/components/ui/menubar.jsx
```

### Feedback Components
```
/app/frontend/src/components/ui/toast.jsx
/app/frontend/src/components/ui/toaster.jsx
/app/frontend/src/components/ui/sonner.jsx
```

---

## Instructions to Main Agent

### 1. Setup & Configuration

#### Install Required Fonts
Add to `/app/frontend/public/index.html` in the `<head>` section:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=Azeret+Mono:wght@500;600;700&display=swap" rel="stylesheet">
```

#### Update CSS Variables
In `/app/frontend/src/index.css`, replace the `:root` section with:
```css
:root {
  /* Colors */
  --primary: 197 100% 44%;           /* #05BFDB */
  --primary-dark: 192 89% 30%;       /* #088395 */
  --primary-darker: 197 85% 22%;     /* #0A4D68 */
  
  --background: 210 40% 98%;         /* #F7FAFC */
  --foreground: 215 25% 27%;         /* #4A5568 */
  
  --card: 0 0% 100%;                 /* #FFFFFF */
  --card-foreground: 215 25% 27%;    /* #4A5568 */
  
  --muted: 210 40% 96%;              /* #F7FAFC */
  --muted-foreground: 215 20% 65%;   /* #A0AEC0 */
  
  --accent: 197 100% 44%;            /* #05BFDB */
  --accent-foreground: 0 0% 100%;    /* #FFFFFF */
  
  --success: 142 71% 45%;            /* #10B981 */
  --error: 348 83% 47%;              /* #F43F5E */
  --warning: 38 92% 50%;             /* #F59E0B */
  
  --border: 214 32% 91%;             /* #E2E8F0 */
  --input: 214 32% 91%;              /* #E2E8F0 */
  --ring: 197 100% 44%;              /* #05BFDB */
  
  --radius: 0.75rem;                 /* 12px */
  
  /* Fonts */
  --font-primary: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-secondary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'Azeret Mono', 'Roboto Mono', monospace;
}
```

#### Update Body Styles
In `/app/frontend/src/index.css`:
```css
body {
  margin: 0;
  font-family: var(--font-secondary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: hsl(var(--background));
  color: hsl(var(--foreground));
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-primary);
  font-weight: 700;
  color: #1A202C;
  letter-spacing: -0.02em;
}
```

### 2. Component Usage Guidelines

#### Always Use data-testid
Every interactive element MUST include `data-testid`:
```jsx
// ✅ Correct
<Button data-testid="start-quiz-button">Start Quiz</Button>
<Card data-testid="quiz-card-1">...</Card>
<input data-testid="username-input" />

// ❌ Incorrect
<Button>Start Quiz</Button>
<Card>...</Card>
<input />
```

#### Button Variants
```jsx
// Primary CTA
<Button data-testid="submit-button" className="btn-primary">
  Submit Answer
</Button>

// Secondary
<Button data-testid="cancel-button" variant="outline" className="btn-secondary">
  Cancel
</Button>

// Ghost
<Button data-testid="skip-button" variant="ghost" className="btn-ghost">
  Skip
</Button>

// Icon
<Button data-testid="close-button" variant="ghost" size="icon">
  <X className="h-5 w-5" />
</Button>
```

#### Card Patterns
```jsx
// Quiz Card
<Card data-testid="quiz-card" className="quiz-card">
  <CardHeader>
    <CardTitle>Daily Quest #1</CardTitle>
    <CardDescription>Geography</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
  <CardFooter>
    <Button data-testid="start-quiz-button">Start</Button>
  </CardFooter>
</Card>

// Locked Quiz Card
<Card data-testid="quiz-card-locked" className="quiz-card quiz-card-locked">
  {/* Same structure */}
</Card>

// Completed Quiz Card
<Card data-testid="quiz-card-completed" className="quiz-card quiz-card-completed">
  {/* Same structure */}
</Card>
```

#### Quiz Interface
```jsx
// Quiz Container
<div className="quiz-container">
  {/* Progress */}
  <div data-testid="quiz-progress" className="progress-container">
    <div className="progress-info">
      <span>Question {current} of {total}</span>
      <span>{percentage}%</span>
    </div>
    <Progress value={percentage} />
  </div>
  
  {/* Timer */}
  <div data-testid="quiz-timer" className="timer-container">
    {/* Timer component */}
  </div>
  
  {/* Question */}
  <div className="quiz-body">
    <h2 className="quiz-question-text">{question}</h2>
    
    {/* Options */}
    <div className="quiz-options">
      {options.map((option, index) => (
        <button
          key={index}
          data-testid={`quiz-option-${index}`}
          className={`quiz-option ${selectedOption === index ? 'selected' : ''}`}
          onClick={() => handleSelect(index)}
        >
          <span className="quiz-option-label">{String.fromCharCode(65 + index)}</span>
          <span className="quiz-option-text">{option}</span>
        </button>
      ))}
    </div>
  </div>
  
  {/* Footer */}
  <div className="quiz-footer">
    <Button data-testid="previous-button" variant="ghost">
      Previous
    </Button>
    <Button data-testid="submit-button" className="btn-primary">
      Submit
    </Button>
  </div>
</div>
```

#### Leaderboard
```jsx
<div className="leaderboard-container">
  <Tabs defaultValue="global" data-testid="leaderboard-tabs">
    <TabsList>
      <TabsTrigger value="global" data-testid="global-tab">Global</TabsTrigger>
      <TabsTrigger value="group" data-testid="group-tab">My Group</TabsTrigger>
    </TabsList>
    
    <TabsContent value="global">
      <div className="leaderboard-list">
        {users.map((user, index) => (
          <Card 
            key={user.id}
            data-testid={`leaderboard-row-${index}`}
            className={`leaderboard-card ${user.isCurrentUser ? 'current-user' : ''}`}
          >
            <CardContent className="leaderboard-row">
              <div className={`leaderboard-rank ${index < 3 ? 'top-3' : ''}`}>
                {index + 1}
              </div>
              <Avatar>
                <AvatarFallback>{user.initials}</AvatarFallback>
              </Avatar>
              <div className="leaderboard-info">
                <p className="leaderboard-name">{user.name}</p>
                <p className="leaderboard-score">{user.score} pts</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </TabsContent>
  </Tabs>
</div>
```

#### Admin Panel Layout
```jsx
<div className="admin-layout">
  {/* Sidebar */}
  <aside className="admin-sidebar" data-testid="admin-sidebar">
    <nav>
      <Button 
        data-testid="nav-dashboard"
        variant="ghost" 
        className="w-full justify-start"
      >
        Dashboard
      </Button>
      <Button 
        data-testid="nav-topics"
        variant="ghost" 
        className="w-full justify-start"
      >
        Topics
      </Button>
      <Button 
        data-testid="nav-questions"
        variant="ghost" 
        className="w-full justify-start"
      >
        Questions
      </Button>
      <Button 
        data-testid="nav-daily-packs"
        variant="ghost" 
        className="w-full justify-start"
      >
        Daily Packs
      </Button>
    </nav>
  </aside>
  
  {/* Main Content */}
  <main className="admin-main">
    <div className="admin-header">
      <h1>Dashboard</h1>
    </div>
    <div className="admin-content">
      {/* Content */}
    </div>
  </main>
</div>
```

### 3. State Management

#### Quiz States
```jsx
// Quiz card states
const quizStates = {
  LOCKED: 'locked',
  AVAILABLE: 'available',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed'
};

// Apply appropriate classes
<Card 
  data-testid="quiz-card"
  className={`quiz-card ${
    state === 'locked' ? 'quiz-card-locked' : 
    state === 'completed' ? 'quiz-card-completed' : ''
  }`}
>
```

#### Answer States
```jsx
// Quiz option states
const answerStates = {
  DEFAULT: '',
  SELECTED: 'selected',
  CORRECT: 'correct',
  INCORRECT: 'incorrect',
  DISABLED: 'disabled'
};

<button
  data-testid={`quiz-option-${index}`}
  className={`quiz-option ${answerStates[currentState]}`}
  disabled={currentState === 'disabled'}
>
```

### 4. Responsive Behavior

#### Mobile-First Approach
Always start with mobile styles, then add tablet and desktop:
```css
/* Mobile (default) */
.component {
  padding: 1rem;
  font-size: 1rem;
}

/* Tablet (≥768px) */
@media (min-width: 768px) {
  .component {
    padding: 1.5rem;
    font-size: 1.125rem;
  }
}

/* Desktop (≥1024px) */
@media (min-width: 1024px) {
  .component {
    padding: 2rem;
    font-size: 1.25rem;
  }
}
```

#### Touch Targets
All interactive elements must be at least 44x44px on mobile:
```css
.touch-target {
  min-height: 44px;
  min-width: 44px;
  padding: 0.75rem 1rem;
}
```

### 5. Animation Guidelines

#### Use Framer Motion for Complex Animations
```bash
npm install framer-motion
```

```jsx
import { motion } from 'framer-motion';

// Page transitions
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -20 }}
  transition={{ duration: 0.3 }}
>
  {/* Content */}
</motion.div>

// Quiz option animation
<motion.button
  whileHover={{ scale: 1.02, x: 4 }}
  whileTap={{ scale: 0.98 }}
  className="quiz-option"
>
  {/* Option content */}
</motion.button>
```

#### CSS Transitions
Keep transitions fast and smooth:
```css
/* Fast transitions for interactive elements */
.interactive {
  transition: all 0.2s ease;
}

/* Slower for layout changes */
.layout-change {
  transition: all 0.3s ease;
}
```

### 6. Toast Notifications

Use Sonner for all toast notifications:
```jsx
import { toast } from 'sonner';

// Success
toast.success('Quiz completed!', {
  description: 'You scored 8 out of 10',
});

// Error
toast.error('Failed to submit answer', {
  description: 'Please try again',
});

// Info
toast.info('New daily quest available!');

// Warning
toast.warning('Only 30 seconds remaining');
```

### 7. Loading States

Always show loading states:
```jsx
import { Skeleton } from '@/components/ui/skeleton';

// Quiz card loading
<Card data-testid="quiz-card-skeleton">
  <CardHeader>
    <Skeleton className="h-6 w-32 mb-2" />
    <Skeleton className="h-4 w-24" />
  </CardHeader>
  <CardContent>
    <Skeleton className="h-20 w-full" />
  </CardContent>
</Card>

// Leaderboard loading
<div className="leaderboard-list">
  {[...Array(5)].map((_, i) => (
    <Card key={i} data-testid={`leaderboard-skeleton-${i}`}>
      <CardContent className="leaderboard-row">
        <Skeleton className="h-8 w-8 rounded-full" />
        <Skeleton className="h-10 w-10 rounded-full" />
        <div className="flex-1">
          <Skeleton className="h-4 w-32 mb-2" />
          <Skeleton className="h-3 w-20" />
        </div>
      </CardContent>
    </Card>
  ))}
</div>
```

### 8. Error States

Provide clear error messages:
```jsx
// Empty state
<div className="empty-state" data-testid="empty-state">
  <img 
    src="https://images.unsplash.com/photo-1560785496-321917f24016" 
    alt="No quizzes available"
    className="empty-state-image"
  />
  <h3>No Quizzes Available</h3>
  <p>Check back tomorrow for new daily quests!</p>
</div>

// Error state
<Alert variant="destructive" data-testid="error-alert">
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>
    Failed to load quiz. Please try again.
  </AlertDescription>
</Alert>
```

### 9. Form Validation

Use shadcn form components with react-hook-form:
```jsx
import { useForm } from 'react-hook-form';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';

const form = useForm();

<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)}>
    <FormField
      control={form.control}
      name="question"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Question</FormLabel>
          <FormControl>
            <Textarea 
              data-testid="question-input"
              placeholder="Enter your question"
              {...field}
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
    <Button data-testid="submit-form-button" type="submit">
      Submit
    </Button>
  </form>
</Form>
```

### 10. PWA Considerations

#### Offline Support
Show offline indicator:
```jsx
const [isOnline, setIsOnline] = useState(navigator.onLine);

useEffect(() => {
  const handleOnline = () => setIsOnline(true);
  const handleOffline = () => setIsOnline(false);
  
  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);
  
  return () => {
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
  };
}, []);

{!isOnline && (
  <Alert data-testid="offline-alert">
    <AlertTitle>You're offline</AlertTitle>
    <AlertDescription>
      Some features may not be available
    </AlertDescription>
  </Alert>
)}
```

#### Install Prompt
```jsx
const [deferredPrompt, setDeferredPrompt] = useState(null);

useEffect(() => {
  const handler = (e) => {
    e.preventDefault();
    setDeferredPrompt(e);
  };
  
  window.addEventListener('beforeinstallprompt', handler);
  
  return () => window.removeEventListener('beforeinstallprompt', handler);
}, []);

const handleInstall = async () => {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    setDeferredPrompt(null);
  }
};
```

---

## Common Mistakes to Avoid

### ❌ Don't:
1. Use dark purple, dark blue, dark pink gradients
2. Apply gradients to more than 20% of viewport
3. Use gradients on small UI elements
4. Forget `data-testid` attributes
5. Skip responsive font sizing
6. Ignore loading and error states
7. Forget hover and focus states
8. Use generic class names
9. Skip accessibility attributes
10. Hardcode colors instead of using CSS variables

### ✅ Do:
1. Keep gradients for hero sections and major CTAs only
2. Use solid colors for content and reading areas
3. Maintain consistent spacing using the spacing system
4. Test on mobile devices with touch interactions
5. Include accessibility features (focus states, contrast, aria labels)
6. Use the pill/capsule button style for primary actions
7. Add `data-testid` to all interactive elements
8. Show loading states with Skeleton components
9. Provide clear error messages
10. Use CSS variables for all colors

---

## Performance Optimization

### Image Optimization
```jsx
// Use lazy loading for images
<img 
  src={imageUrl}
  alt={description}
  loading="lazy"
  className="optimized-image"
/>

// Use appropriate image sizes
.optimized-image {
  max-width: 100%;
  height: auto;
  object-fit: cover;
}
```

### Code Splitting
```jsx
// Lazy load routes
import { lazy, Suspense } from 'react';

const AdminPanel = lazy(() => import('./pages/AdminPanel'));

<Suspense fallback={<LoadingSpinner />}>
  <AdminPanel />
</Suspense>
```

### Debounce Search
```jsx
import { useDebouncedCallback } from 'use-debounce';

const handleSearch = useDebouncedCallback((value) => {
  // Search logic
}, 300);
```

---

## Testing Guidelines

### Component Testing
```jsx
// Always use data-testid for testing
import { render, screen, fireEvent } from '@testing-library/react';

test('quiz option can be selected', () => {
  render(<QuizOption />);
  
  const option = screen.getByTestId('quiz-option-0');
  fireEvent.click(option);
  
  expect(option).toHaveClass('selected');
});
```

### Accessibility Testing
```jsx
// Test keyboard navigation
test('button is keyboard accessible', () => {
  render(<Button data-testid="submit-button">Submit</Button>);
  
  const button = screen.getByTestId('submit-button');
  button.focus();
  
  expect(button).toHaveFocus();
});
```

---

## Additional Libraries

### Recommended Installations
```bash
# Animations
npm install framer-motion

# Form handling
npm install react-hook-form @hookform/resolvers zod

# Date handling (if needed for calendar)
npm install date-fns

# Icons (already installed)
npm install lucide-react

# Toast notifications (already installed)
npm install sonner

# Utilities
npm install clsx tailwind-merge
```

### Optional Enhancements
```bash
# Charts for admin dashboard
npm install recharts

# Confetti for celebrations
npm install canvas-confetti

# Sound effects
npm install use-sound
```

---

## Brand Integration

### Socrates Silhouette
Create a custom logo component with question mark integration:
```jsx
// components/Logo.jsx
export const Logo = ({ className }) => (
  <div className={`logo ${className}`} data-testid="app-logo">
    <svg viewBox="0 0 100 100" className="logo-svg">
      {/* Socrates silhouette with question mark */}
      <path d="M50,10 C30,10 20,25 20,40 C20,55 30,65 40,70 L40,80 L45,90 L55,90 L60,80 L60,70 C70,65 80,55 80,40 C80,25 70,10 50,10 Z" fill="currentColor" />
      <text x="50" y="55" fontSize="40" textAnchor="middle" fill="#FFFFFF">?</text>
    </svg>
    <span className="logo-text">SocraQuest</span>
  </div>
);

// CSS
.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-svg {
  width: 40px;
  height: 40px;
  color: #088395;
}

.logo-text {
  font-family: var(--font-primary);
  font-weight: 700;
  font-size: 1.5rem;
  color: #0A4D68;
}
```

---

## Final Checklist

Before considering a screen complete, verify:

- [ ] All interactive elements have `data-testid` attributes
- [ ] Mobile-first responsive design implemented
- [ ] Loading states with Skeleton components
- [ ] Error states with clear messages
- [ ] Empty states with helpful content
- [ ] Hover states on interactive elements
- [ ] Focus states for keyboard navigation
- [ ] ARIA labels for screen readers
- [ ] Color contrast meets WCAG AA
- [ ] Touch targets are at least 44x44px
- [ ] Animations are smooth and purposeful
- [ ] Gradients limited to 20% of viewport
- [ ] Images are lazy loaded
- [ ] Forms have validation
- [ ] Toast notifications for feedback
- [ ] Consistent spacing using design tokens
- [ ] Typography follows the scale
- [ ] Colors use CSS variables

---

## Support & Resources

### Documentation Links
- shadcn/ui: https://ui.shadcn.com
- Tailwind CSS: https://tailwindcss.com
- Framer Motion: https://www.framer.com/motion
- React Hook Form: https://react-hook-form.com
- Lucide Icons: https://lucide.dev

### Design References
- Quizzo UI Kit: https://www.behance.net/gallery/160302285/Quizzo-Quiz-App-UI-Kit
- Material Design: https://m3.material.io
- Apple Human Interface Guidelines: https://developer.apple.com/design

---

# General UI UX Design Guidelines

## Universal Transition Rule
- You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms

## Text Alignment Rule
- You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text

## Icon Usage Rule
- NEVER use AI assistant Emoji characters like `🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇` etc for icons
- Always use **lucide-react** library (already installed) for all icons
- Example: `import { Trophy, Star, Lock } from 'lucide-react'`

## Gradient Restriction Rule (CRITICAL)
- NEVER use dark/saturated gradient combos (e.g., purple/pink, blue-500 to purple-600, red to pink)
- NEVER use dark gradients for logo, testimonial, footer
- NEVER let gradients cover more than 20% of the viewport
- NEVER apply gradients to text-heavy content or reading areas
- NEVER use gradients on small UI elements (<100px width)
- NEVER stack multiple gradient layers in the same viewport

### Enforcement Rule
IF gradient area exceeds 20% of viewport OR affects readability
THEN use solid colors

### How and Where to Use Gradients
- Section backgrounds (not content backgrounds)
- Hero section header content (dark to light to dark color)
- Decorative overlays and accent elements only
- Hero section with 2-3 mild colors
- Gradients can be horizontal, vertical, or diagonal

## Color Usage for AI Applications
- For AI chat, voice applications, **do not use purple color**
- Use colors like light green, ocean blue, peach orange, teal, cyan

## Micro-Interactions Rule
- Every interaction needs micro-animations
- Hover states, transitions, entrance animations
- Static = dead

## Spacing Rule
- Use 2-3x more spacing than feels comfortable
- Cramped designs look cheap
- Follow the spacing system defined above

## Visual Polish
- Subtle grain textures, noise overlays
- Custom cursors (optional)
- Selection states
- Loading animations
- Separates good from extraordinary

## Design Token Instantiation
- Before generating UI, infer the visual style from the problem statement
- Immediately set global design tokens (primary, secondary, background, foreground, ring, state colors)
- Don't rely on library defaults
- Don't make background dark as default - understand problem first

## Component Reuse Priority
1. Prioritize using pre-existing components from `/app/frontend/src/components/ui/`
2. Create new components that match existing style and conventions
3. Examine existing components before creating new ones

## Component Library Rule
- Do not use HTML-based components like dropdown, calendar, toast
- You **MUST** always use `/app/frontend/src/components/ui/` components only
- These are modern, stylish, and accessible

## Export Conventions
- Components MUST use named exports: `export const ComponentName = ...`
- Pages MUST use default exports: `export default function PageName() {...}`

## Toast Notifications
- Use `sonner` for all toasts
- Sonner component located at `/app/frontend/src/components/ui/sonner.jsx`

## Gradient Creation
- Use 2-4 color gradients
- Subtle textures/noise overlays
- CSS-based noise to avoid flat visuals

## Testing Attributes (CRITICAL)
- All interactive and key informational elements **MUST** include a `data-testid` attribute
- This applies to buttons, links, form inputs, menus, and any element that displays critical information
- Use kebab-case convention that defines the element's role, not appearance
- Example: `data-testid="login-form-submit-button"`
- This creates a stable interface for tests, preventing breakage from style changes

---

**End of Design Guidelines**

This comprehensive design system ensures SocraQuest delivers a sophisticated, engaging, and accessible quiz experience that motivates users while maintaining professional standards. All components are mobile-first, PWA-ready, and optimized for performance.