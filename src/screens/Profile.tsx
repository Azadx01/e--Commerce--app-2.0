import React, { useState } from 'react';
import { View, StyleSheet, SafeAreaView, Text, Alert } from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { HomeStackParamList } from '../navigation/types';
import { Header, Button, Card, Loading } from '../components';
import { theme } from '../theme/theme';
import { useAuth } from '../store/authStore';
import { ApiError } from '../services/apiClient';

type Props = {
    navigation: NativeStackNavigationProp<HomeStackParamList, 'Profile'>;
};

export const Profile = ({ navigation }: Props) => {
    const { user, signOut } = useAuth();
    const [loading, setLoading] = useState(false);

    const handleLogout = () => {
        Alert.alert('Log Out', 'Are you sure you want to log out?', [
            { text: 'Cancel', style: 'cancel' },
            {
                text: 'Log Out',
                style: 'destructive',
                onPress: async () => {
                    setLoading(true);
                    try {
                        await signOut();
                        // AppNavigator automatically switches back to AuthStack
                    } catch (err) {
                        const msg = err instanceof ApiError ? err.detail : 'Logout failed.';
                        Alert.alert('Error', msg);
                    } finally {
                        setLoading(false);
                    }
                },
            },
        ]);
    };

    if (loading) return <Loading />;

    return (
        <SafeAreaView style={styles.container}>
            <Header title="My Profile" />
            <View style={styles.content}>
                <Card style={styles.card}>
                    <Text style={styles.label}>Name</Text>
                    <Text style={styles.value}>{user?.name ?? '—'}</Text>
                    <View style={styles.divider} />
                    <Text style={styles.label}>Email</Text>
                    <Text style={styles.value}>{user?.email ?? '—'}</Text>
                    <View style={styles.divider} />
                    <Text style={styles.label}>Role</Text>
                    <Text style={styles.value}>{user?.role ?? '—'}</Text>
                    <View style={styles.divider} />
                    <Text style={styles.label}>Account Status</Text>
                    <Text style={[styles.value, user?.status === 'active' ? styles.statusActive : styles.statusOther]}>
                        {user?.status ?? '—'}
                    </Text>
                </Card>

                <View style={styles.spacer} />
                <Button
                    title="Back to Dashboard"
                    variant="outline"
                    onPress={() => navigation.goBack()}
                />
                <Button
                    title="Log Out"
                    variant="primary"
                    onPress={handleLogout}
                />
            </View>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    content: { flex: 1, padding: theme.spacing.m },
    card: { padding: theme.spacing.xl },
    label: { ...theme.typography.caption, color: theme.colors.textSecondary, marginBottom: 2 },
    value: { ...theme.typography.body, color: theme.colors.text, marginBottom: theme.spacing.m },
    divider: { height: 1, backgroundColor: theme.colors.border, marginVertical: theme.spacing.s },
    statusActive: { color: theme.colors.success },
    statusOther: { color: theme.colors.error },
    spacer: { height: theme.spacing.xl },
});
