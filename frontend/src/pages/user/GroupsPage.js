import React, { useState, useEffect } from 'react';
import { userAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { Trophy, Plus, UserPlus, Users as UsersIcon } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';
import { getInitials } from '../../lib/utils';

export function GroupsPage() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [joinOpen, setJoinOpen] = useState(false);
  const [groupName, setGroupName] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [creating, setCreating] = useState(false);
  const [joining, setJoining] = useState(false);

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      const res = await userAPI.getGroups();
      setGroups(res.data.groups);
    } catch (error) {
      toast.error('Failed to load groups');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      await userAPI.createGroup({ name: groupName });
      toast.success('Group created successfully!');
      setGroupName('');
      setCreateOpen(false);
      loadGroups();
    } catch (error) {
      toast.error('Failed to create group');
    } finally {
      setCreating(false);
    }
  };

  const handleJoinGroup = async (e) => {
    e.preventDefault();
    setJoining(true);
    try {
      await userAPI.joinGroup({ code: joinCode });
      toast.success('Joined group successfully!');
      setJoinCode('');
      setJoinOpen(false);
      loadGroups();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to join group');
    } finally {
      setJoining(false);
    }
  };

  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-slate-900 font-['Space_Grotesk']">My Groups</h1>
        <div className="flex space-x-2">
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-teal-500 to-teal-600" data-testid="create-group-button">
                <Plus className="w-4 h-4 mr-2" />
                Create
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Group</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateGroup} className="space-y-4">
                <div>
                  <Label htmlFor="groupName">Group Name</Label>
                  <Input
                    id="groupName"
                    value={groupName}
                    onChange={(e) => setGroupName(e.target.value)}
                    placeholder="Enter group name"
                    required
                    data-testid="group-name-input"
                  />
                </div>
                <Button type="submit" disabled={creating} className="w-full" data-testid="create-group-submit">
                  {creating ? 'Creating...' : 'Create Group'}
                </Button>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={joinOpen} onOpenChange={setJoinOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" data-testid="join-group-button">
                <UserPlus className="w-4 h-4 mr-2" />
                Join
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Join Group</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleJoinGroup} className="space-y-4">
                <div>
                  <Label htmlFor="joinCode">Group Code</Label>
                  <Input
                    id="joinCode"
                    value={joinCode}
                    onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                    placeholder="Enter group code"
                    required
                    data-testid="join-code-input"
                  />
                </div>
                <Button type="submit" disabled={joining} className="w-full" data-testid="join-group-submit">
                  {joining ? 'Joining...' : 'Join Group'}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Groups List */}
      {groups.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-slate-200">
          <UsersIcon className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">No groups yet</h3>
          <p className="text-slate-600 mb-4">Create or join a group to compete with friends!</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {groups.map((group) => (
            <div key={group._id} className="bg-white rounded-xl p-6 border border-slate-200 hover:border-teal-300 transition-all" data-testid={`group-card-${group._id}`}>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 font-['Space_Grotesk']">{group.name}</h3>
                  <p className="text-sm text-slate-600">{group.member_count} members</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500 mb-1">Group Code</p>
                  <p className="text-lg font-mono font-bold text-teal-600">{group.code}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
