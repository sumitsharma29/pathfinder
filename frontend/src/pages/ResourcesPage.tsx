import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Search,
  Filter,
  ExternalLink,
  Clock,
  Award,
  Layers,
  ChevronLeft,
  ChevronRight,
  Info
} from 'lucide-react';
import { api } from '../api/client';
import { PaginatedResourcesResponse, ResourceCatalogItem, Skill } from '../types/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner, ErrorMessage, EmptyState } from '../components/common/FeedbackStates';

export const ResourcesPage: React.FC = () => {
  const [data, setData] = useState<PaginatedResourcesResponse | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [page, setPage] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedSkillId, setSelectedSkillId] = useState<string>('');
  const [selectedResource, setSelectedResource] = useState<ResourceCatalogItem | null>(null);

  const fetchResources = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.getResources({
        page,
        page_size: 12,
        q: searchQuery || undefined,
        difficulty: selectedDifficulty || undefined,
        resource_type: selectedType || undefined,
        skill_id: selectedSkillId || undefined,
      });
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load resources catalog');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    api.getSkills().then(setSkills).catch(console.error);
  }, []);

  useEffect(() => {
    fetchResources();
  }, [page, selectedDifficulty, selectedType, selectedSkillId]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchResources();
  };

  const handleInspectDetail = async (id: string) => {
    try {
      const detail = await api.getResource(id);
      setSelectedResource(detail);
    } catch (e) {
      alert('Failed to load resource details');
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Curated Learning Resource Catalog
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Explore validated courses, tutorials, articles, and documentation aligned with industry standards
        </p>
      </div>

      {/* Filter & Search Bar */}
      <Card className="p-4 sm:p-5 space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search resources by title, topic, or keyword..."
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2 pl-10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>
          <Button type="submit" size="md">
            Search
          </Button>
        </form>

        <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-slate-800 text-xs">
          <span className="text-slate-400 font-medium flex items-center gap-1.5">
            <Filter className="w-3.5 h-3.5 text-emerald-400" /> Filters:
          </span>

          <select
            value={selectedDifficulty}
            onChange={(e) => {
              setSelectedDifficulty(e.target.value);
              setPage(1);
            }}
            className="bg-slate-900 border border-slate-700 text-white rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Difficulties</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>

          <select
            value={selectedType}
            onChange={(e) => {
              setSelectedType(e.target.value);
              setPage(1);
            }}
            className="bg-slate-900 border border-slate-700 text-white rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Types</option>
            <option value="course">Course</option>
            <option value="article">Article</option>
            <option value="video">Video</option>
            <option value="documentation">Documentation</option>
            <option value="book">Book</option>
            <option value="project">Project</option>
          </select>

          <select
            value={selectedSkillId}
            onChange={(e) => {
              setSelectedSkillId(e.target.value);
              setPage(1);
            }}
            className="bg-slate-900 border border-slate-700 text-white rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:border-emerald-500 max-w-[200px]"
          >
            <option value="">All Skills</option>
            {skills.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>

          {(selectedDifficulty || selectedType || selectedSkillId || searchQuery) && (
            <button
              onClick={() => {
                setSelectedDifficulty('');
                setSelectedType('');
                setSelectedSkillId('');
                setSearchQuery('');
                setPage(1);
              }}
              className="text-xs text-rose-400 hover:underline ml-auto"
            >
              Reset Filters
            </button>
          )}
        </div>
      </Card>

      {error && <ErrorMessage title="Failed to load catalog" message={error} onRetry={fetchResources} />}

      {/* Catalog Grid */}
      {isLoading ? (
        <LoadingSpinner message="Searching verified catalog..." size="lg" />
      ) : data?.items && data.items.length > 0 ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {data.items.map((res) => (
              <Card key={res.id} hoverEffect className="flex flex-col justify-between p-5 space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Badge variant="default" size="sm">
                      {res.resource_type.toUpperCase()}
                    </Badge>
                    <span className="text-xs font-semibold text-slate-400 capitalize">{res.difficulty || 'All Levels'}</span>
                  </div>

                  <h3 className="text-base font-bold text-white leading-snug line-clamp-2">{res.title}</h3>
                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {res.description || 'Curated high-yield learning resource.'}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <div className="flex items-center gap-3">
                    {res.estimated_minutes && (
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-slate-500" /> {Math.round(res.estimated_minutes / 60)}h
                      </span>
                    )}
                    {res.quality_score && (
                      <span className="flex items-center gap-1 font-mono text-emerald-400">
                        <Award className="w-3.5 h-3.5" /> {res.quality_score}%
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleInspectDetail(res.id)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                      title="Inspect Resource"
                    >
                      <Info className="w-4 h-4" />
                    </button>
                    <a
                      href={res.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-400 hover:text-emerald-300 transition"
                    >
                      Visit <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination Controls */}
          {data.pages > 1 && (
            <div className="flex items-center justify-between pt-4 border-t border-slate-800">
              <span className="text-xs text-slate-400">
                Showing Page {data.page} of {data.pages} ({data.total} resources total)
              </span>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage(page - 1)}
                >
                  <ChevronLeft className="w-4 h-4 mr-1" /> Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= data.pages}
                  onClick={() => setPage(page + 1)}
                >
                  Next <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          icon={<BookOpen className="w-8 h-8" />}
          title="No Resources Matched"
          description="Try broadening your search query or removing difficulty and skill filters."
        />
      )}

      {/* Resource Detail Modal */}
      <Modal
        isOpen={!!selectedResource}
        onClose={() => setSelectedResource(null)}
        title={selectedResource?.title || 'Resource Details'}
      >
        {selectedResource && (
          <div className="space-y-4">
            <p className="text-sm text-slate-300 leading-relaxed">
              {selectedResource.description || 'Curated high-yield resource for targeted skill mastery.'}
            </p>

            <div className="grid grid-cols-2 gap-3 p-3 bg-slate-900 rounded-xl border border-slate-800 text-xs">
              <div>
                <span className="text-slate-500">Provider:</span>{' '}
                <span className="text-white font-medium">{selectedResource.provider || 'Self-paced'}</span>
              </div>
              <div>
                <span className="text-slate-500">Difficulty:</span>{' '}
                <span className="text-white capitalize font-medium">{selectedResource.difficulty || 'All Levels'}</span>
              </div>
              <div>
                <span className="text-slate-500">Estimated Duration:</span>{' '}
                <span className="text-white font-medium">{selectedResource.estimated_minutes ? `${selectedResource.estimated_minutes} mins` : 'N/A'}</span>
              </div>
              <div>
                <span className="text-slate-500">Quality Score:</span>{' '}
                <span className="text-emerald-400 font-mono font-bold">{selectedResource.quality_score ? `${selectedResource.quality_score}%` : 'N/A'}</span>
              </div>
            </div>

            {selectedResource.skills && selectedResource.skills.length > 0 && (
              <div>
                <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Skills Covered</h5>
                <div className="flex flex-wrap gap-1.5">
                  {selectedResource.skills.map((s) => (
                    <span key={s.id} className="text-xs px-2.5 py-1 rounded-md bg-slate-800 text-slate-200 border border-slate-700">
                      {s.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between pt-4 border-t border-slate-800">
              <Button variant="ghost" onClick={() => setSelectedResource(null)}>
                Close
              </Button>
              <a
                href={selectedResource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition shadow-lg shadow-emerald-500/20"
              >
                Launch Learning Resource <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
