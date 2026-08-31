import React, { useState, useEffect } from 'react';
import {
  CheckSquare,
  Play,
  CheckCircle2,
  XCircle,
  Sparkles,
  History
} from 'lucide-react';
import { api } from '../api/client';
import {
  AssessmentSummaryItem,
  AssessmentDetail,
  AssessmentResultResponse,
  AssessmentHistoryItem
} from '../types/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner, ErrorMessage } from '../components/common/FeedbackStates';

export const AssessmentsPage: React.FC = () => {
  const [assessments, setAssessments] = useState<AssessmentSummaryItem[]>([]);
  const [history, setHistory] = useState<AssessmentHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Active Quiz State
  const [activeQuiz, setActiveQuiz] = useState<AssessmentDetail | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [quizResult, setQuizResult] = useState<AssessmentResultResponse | null>(null);

  const fetchAssessmentsData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [list, results] = await Promise.all([
        api.getAssessments(),
        api.getAssessmentResults().catch(() => []),
      ]);
      setAssessments(list);
      setHistory(results);
    } catch (err: any) {
      setError(err.message || 'Failed to load assessments');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAssessmentsData();
  }, []);

  const handleStartAssessment = async (id: string) => {
    setIsLoading(true);
    try {
      const detail = await api.getAssessment(id);
      setActiveQuiz(detail);
      setSelectedAnswers({});
      setQuizResult(null);
    } catch (err: any) {
      alert(err.message || 'Failed to load assessment questions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptionSelect = (questionId: string, answerText: string) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionId]: answerText,
    });
  };

  const handleSubmitQuiz = async () => {
    if (!activeQuiz) return;

    // Verify all answered
    if (Object.keys(selectedAnswers).length < activeQuiz.questions.length) {
      if (!confirm('You have unanswered questions. Are you sure you want to submit?')) {
        return;
      }
    }

    setIsSubmitting(true);
    try {
      const answersPayload = Object.entries(selectedAnswers).map(([qid, ans]) => ({
        question_id: qid,
        answer: ans,
      }));

      const res = await api.submitAssessment(activeQuiz.id, answersPayload);
      setQuizResult(res);
      await fetchAssessmentsData(); // Refresh history
    } catch (err: any) {
      alert(err.message || 'Failed to submit assessment answers');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading && !activeQuiz) {
    return <LoadingSpinner message="Loading assessment center..." size="lg" />;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Knowledge Assessments & Verification
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Validate your skills with server-graded assessments to adapt your learning path
        </p>
      </div>

      {error && <ErrorMessage title="Assessment Error" message={error} onRetry={fetchAssessmentsData} />}

      {/* Available Assessments Grid */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <CheckSquare className="w-5 h-5 text-emerald-400" />
          Available Skill Tests
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {assessments.map((a) => (
            <Card key={a.id} hoverEffect className="flex flex-col justify-between p-5 space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Badge variant="purple" size="sm">
                    {a.skill?.name || 'Skill Assessment'}
                  </Badge>
                  <span className="text-xs text-slate-400 font-mono">
                    Pass: {a.passing_score}%
                  </span>
                </div>
                <h4 className="text-base font-bold text-white leading-snug">{a.title}</h4>
                <p className="text-xs text-slate-400">
                  {a.question_count} Questions • Server-side graded
                </p>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <span className="text-xs text-slate-400 font-medium">Difficulty: {a.difficulty || 'Intermediate'}</span>
                <Button size="sm" onClick={() => handleStartAssessment(a.id)}>
                  <Play className="w-3.5 h-3.5 mr-1" /> Take Test
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Assessment History Table */}
      {history.length > 0 && (
        <Card className="p-6 space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-blue-400" />
            Your Verification History
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="pb-3 px-2">Assessment</th>
                  <th className="pb-3 px-2">Attempt</th>
                  <th className="pb-3 px-2">Score</th>
                  <th className="pb-3 px-2">Mastery</th>
                  <th className="pb-3 px-2">Result</th>
                  <th className="pb-3 px-2 text-right">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {history.map((h) => (
                  <tr key={h.id} className="hover:bg-slate-900/40 transition">
                    <td className="py-3 px-2 font-semibold text-white">{h.assessment_title}</td>
                    <td className="py-3 px-2 font-mono text-slate-400">#{h.attempt_number}</td>
                    <td className="py-3 px-2 font-mono font-bold text-white">{h.score}%</td>
                    <td className="py-3 px-2 font-mono font-bold text-emerald-400">{h.skill_mastery}%</td>
                    <td className="py-3 px-2">
                      <Badge variant={h.passed ? 'success' : 'danger'} size="sm">
                        {h.passed ? 'PASSED' : 'FAILED'}
                      </Badge>
                    </td>
                    <td className="py-3 px-2 text-right text-slate-400">
                      {new Date(h.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Active Assessment Quiz Modal */}
      <Modal
        isOpen={!!activeQuiz}
        onClose={() => {
          if (confirm('Are you sure you want to exit the assessment?')) {
            setActiveQuiz(null);
            setQuizResult(null);
          }
        }}
        title={activeQuiz?.title || 'Skill Assessment'}
        maxWidth="2xl"
      >
        {activeQuiz && (
          <div className="space-y-6">
            {!quizResult ? (
              <>
                <div className="flex items-center justify-between p-3 bg-slate-900 rounded-xl border border-slate-800 text-xs">
                  <span className="text-slate-400">
                    Skill: <strong className="text-white">{activeQuiz.skill?.name || 'Technical Skill'}</strong>
                  </span>
                  <span className="text-slate-400">
                    Passing Criteria: <strong className="text-emerald-400">{activeQuiz.passing_score}%</strong>
                  </span>
                </div>

                {/* Questions List */}
                <div className="space-y-6 max-h-[60vh] overflow-y-auto pr-2">
                  {activeQuiz.questions.map((q, idx) => (
                    <div key={q.id} className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 space-y-3">
                      <h4 className="text-sm font-semibold text-white">
                        {idx + 1}. {q.question}
                      </h4>

                      <div className="space-y-2">
                        {q.options && typeof q.options === 'object' ? (
                          Object.entries(q.options).map(([optKey, optVal]) => {
                            const valStr = String(optVal);
                            const isSelected = selectedAnswers[q.id] === valStr || selectedAnswers[q.id] === optKey;

                            return (
                              <button
                                key={optKey}
                                type="button"
                                onClick={() => handleOptionSelect(q.id, valStr)}
                                className={`w-full text-left p-3 rounded-xl text-xs transition border flex items-center justify-between ${
                                  isSelected
                                    ? 'bg-emerald-500/10 border-emerald-500 text-emerald-300 font-semibold'
                                    : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
                                }`}
                              >
                                <span>{valStr}</span>
                                {isSelected && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />}
                              </button>
                            );
                          })
                        ) : (
                          <input
                            type="text"
                            value={selectedAnswers[q.id] || ''}
                            onChange={(e) => handleOptionSelect(q.id, e.target.value)}
                            placeholder="Type your answer..."
                            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                          />
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                  <span className="text-xs text-slate-400 font-mono">
                    Answered: {Object.keys(selectedAnswers).length} / {activeQuiz.questions.length}
                  </span>
                  <Button onClick={handleSubmitQuiz} isLoading={isSubmitting} size="md">
                    Submit Answers for Scoring
                  </Button>
                </div>
              </>
            ) : (
              /* Assessment Results Screen */
              <div className="text-center py-6 space-y-6">
                <div
                  className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto text-2xl font-bold shadow-2xl ${
                    quizResult.passed
                      ? 'bg-emerald-950 text-emerald-400 border border-emerald-600'
                      : 'bg-rose-950 text-rose-400 border border-rose-600'
                  }`}
                >
                  {quizResult.passed ? <CheckCircle2 className="w-10 h-10" /> : <XCircle className="w-10 h-10" />}
                </div>

                <div>
                  <h3 className="text-2xl font-extrabold text-white">
                    {quizResult.passed ? 'Assessment Passed!' : 'Assessment Incomplete'}
                  </h3>
                  <p className="text-sm text-slate-400 mt-1">
                    You scored <strong className="text-white font-mono text-base">{quizResult.score}%</strong> ({quizResult.correct_count}/{quizResult.total_questions} correct • Pass: {activeQuiz.passing_score}%)
                  </p>
                </div>

                <div className="glass-card rounded-xl p-4 border border-slate-800 text-left text-xs max-w-md mx-auto space-y-1.5">
                  <p className="text-slate-400">
                    Skill Mastery Calculated:{' '}
                    <strong className="text-white">{quizResult.skill_name}</strong>
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Attempt #{quizResult.attempt_number}</span>
                    <span className="text-emerald-400 font-bold font-mono">
                      Mastery: {quizResult.skill_mastery}%
                    </span>
                  </div>
                </div>

                <div className="flex justify-center gap-3 pt-4">
                  <Button
                    onClick={() => {
                      setActiveQuiz(null);
                      setQuizResult(null);
                    }}
                  >
                    Return to Assessments
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};
