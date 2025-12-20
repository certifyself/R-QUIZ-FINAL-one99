import React, { useState, useEffect } from 'react';
import { userAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { Trophy, Plus, UserPlus, Users as UsersIcon, Mail, MessageCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { toast } from 'sonner';
import { getInitials } from '../../lib/utils';
import { useTranslation } from 'react-i18next';

export function GroupsPage() {
  const { t } = useTranslation();
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [joinOpen, setJoinOpen] = useState(false);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [groupName, setGroupName] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteMessage, setInviteMessage] = useState('');
  const [creating, setCreating] = useState(false);
  const [joining, setJoining] = useState(false);
  const [inviting, setInviting] = useState(false);

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
      console.error('Join group error:', error.response?.data);
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'Failed to join group';
      toast.error(typeof errorMsg === 'string' ? errorMsg : 'Failed to join group. Please check the code.');
    } finally {
      setJoining(false);
    }
  };


  const handleInvite = async (e) => {
    e.preventDefault();
    if (!inviteEmail || !selectedGroup) return;

    setInviting(true);
    try {
      await userAPI.sendGroupInvite(selectedGroup._id, inviteEmail, inviteMessage);
      toast.success(`Invitation sent to ${inviteEmail}!`);
      setInviteEmail('');
      setInviteMessage('');
      setInviteOpen(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setInviting(false);
    }
  };

  const openInviteDialog = (group) => {
    setSelectedGroup(group);
    setInviteMessage(`Join my group "${group.name}" on SocraQuest! Let's compete and have fun together.`);
    setInviteOpen(true);
  };

  const handleWhatsAppInvite = (group) => {
    const inviteUrl = `https://socraquest.preview.emergentagent.com/groups/join/${group.code}`;
    const message = `🎮 *Join my SocraQuest group!*\n\n` +
      `Group: *${group.name}*\n` +
      `Code: *${group.code}*\n\n` +
      `Let's compete and have fun together!\n\n` +
      `Click to join: ${inviteUrl}`;
    
    // Open WhatsApp with pre-filled message
    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
    window.open(whatsappUrl, '_blank');
    toast.success('WhatsApp opened! Send to your friends.');
  };


  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-slate-900 font-['Space_Grotesk']">{t('groups.title')}</h1>
        <div className="flex space-x-2">
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-teal-500 to-teal-600" data-testid="create-group-button">
                <Plus className="w-4 h-4 mr-2" />
                {t('groups.create')}
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t('groups.create_group')}</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateGroup} className="space-y-4">
                <div>
                  <Label htmlFor="groupName">{t('groups.group_name')}</Label>
                  <Input
                    id="groupName"
                    value={groupName}
                    onChange={(e) => setGroupName(e.target.value)}
                    placeholder={t('groups.enter_name')}
                    required
                    data-testid="group-name-input"
                  />
                </div>
                <Button type="submit" disabled={creating} className="w-full" data-testid="create-group-submit">
                  {creating ? t('groups.creating') : t('groups.create_group')}
                </Button>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={joinOpen} onOpenChange={setJoinOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" data-testid="join-group-button">
                <UserPlus className="w-4 h-4 mr-2" />
                {t('groups.join')}
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t('groups.join_group')}</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleJoinGroup} className="space-y-4">
                <div>
                  <Label htmlFor="joinCode">{t('groups.group_code')}</Label>
                  <Input
                    id="joinCode"
                    value={joinCode}
                    onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                    placeholder={t('groups.enter_code')}
                    required
                    data-testid="join-code-input"
                  />
                </div>
                <Button type="submit" disabled={joining} className="w-full" data-testid="join-group-submit">
                  {joining ? t('groups.joining') : t('groups.join_group')}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>


      {/* Invite Dialog */}
      <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('groups.invite_friends_to')} {selectedGroup?.name}</DialogTitle>
          </DialogHeader>
          
          {/* Note about email service */}
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4">
            <p className="text-sm text-amber-900">
              ⚠️ <strong>{t('groups.note')}:</strong> {t('groups.email_not_configured')}
              <br/>
              <strong>{t('groups.tip')}:</strong> {t('groups.use_whatsapp')}
            </p>
          </div>
          
          <form onSubmit={handleInvite} className="space-y-4">
            <div>
              <Label htmlFor="invite-email">{t('groups.friend_email')}</Label>
              <Input
                id="invite-email"
                type="email"
                placeholder={t('groups.email_placeholder')}
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                required
              />
            </div>
            
            <div>
              <Label htmlFor="invite-message">{t('groups.personal_message')}</Label>
              <Textarea
                id="invite-message"
                placeholder={t('groups.message_placeholder')}
                value={inviteMessage}
                onChange={(e) => setInviteMessage(e.target.value)}
                rows={4}
              />
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-xs text-blue-900 mb-1 font-medium">{t('groups.group_code')}:</p>
              <p className="text-lg font-mono font-bold text-blue-700">{selectedGroup?.code}</p>
              <p className="text-xs text-blue-600 mt-1">{t('groups.share_code')}</p>
            </div>
            
            <Button 
              type="submit" 
              disabled={inviting}
              className="w-full bg-gradient-to-r from-teal-500 to-teal-600"
            >
              {inviting ? t('groups.sending') : t('groups.send_invitation')}
            </Button>
          </form>
        </DialogContent>
      </Dialog>


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
              
              {/* Invite Buttons */}
              <div className="flex gap-2">
                <Button
                  onClick={() => openInviteDialog(group)}
                  variant="outline"
                  className="flex-1 border-teal-300 text-teal-700 hover:bg-teal-50"
                  data-testid="invite-email-button"
                >
                  <Mail className="w-4 h-4 mr-2" />
                  Email
                </Button>
                
                <Button
                  onClick={() => handleWhatsAppInvite(group)}
                  variant="outline"
                  className="flex-1 border-green-300 text-green-700 hover:bg-green-50"
                  data-testid="invite-whatsapp-button"
                >
                  <MessageCircle className="w-4 h-4 mr-2" />
                  WhatsApp
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
