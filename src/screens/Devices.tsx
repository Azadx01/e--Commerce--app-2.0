import React, { useCallback, useEffect, useState } from 'react';
import {
    View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, Alert
} from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useFocusEffect } from '@react-navigation/native';
import { HomeStackParamList } from '../navigation/types';
import { Header, Button, EmptyState, Loading, ErrorMessage, Card } from '../components';
import { theme } from '../theme/theme';
import { deviceService, DeviceRead } from '../services/deviceService';
import { ApiError } from '../services/apiClient';

type Props = {
    navigation: NativeStackNavigationProp<HomeStackParamList, 'Devices'>;
};

const CATEGORY_ICON: Record<string, string> = {
    smartphone: '📱',
    laptop: '💻',
};

export const Devices = ({ navigation }: Props) => {
    const [devices, setDevices] = useState<DeviceRead[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchDevices = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const data = await deviceService.list();
            setDevices(data);
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.detail);
            } else {
                setError('Failed to load devices.');
            }
        } finally {
            setLoading(false);
        }
    }, []);

    // Refresh list every time the screen comes into focus
    useFocusEffect(
        useCallback(() => {
            fetchDevices();
        }, [fetchDevices])
    );

    const handleDelete = (device: DeviceRead) => {
        Alert.alert(
            'Delete Device',
            `Are you sure you want to remove "${device.brand} ${device.model}"?`,
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Delete',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            await deviceService.remove(device.id);
                            setDevices((prev) => prev.filter((d) => d.id !== device.id));
                        } catch (err) {
                            const msg = err instanceof ApiError ? err.detail : 'Delete failed.';
                            Alert.alert('Error', msg);
                        }
                    },
                },
            ]
        );
    };

    if (loading) return <Loading />;

    return (
        <SafeAreaView style={styles.container}>
            <Header title="My Devices" />
            <ScrollView contentContainerStyle={styles.content}>
                {error ? <ErrorMessage message={error} /> : null}

                {devices.length === 0 && !error ? (
                    <EmptyState
                        title="No Devices Found"
                        description="Register your smartphone or laptop to start getting repair or resale estimates."
                    />
                ) : (
                    devices.map((device) => (
                        <Card key={device.id} style={styles.card}>
                            <View style={styles.cardHeader}>
                                <Text style={styles.icon}>
                                    {CATEGORY_ICON[device.category] ?? '📦'}
                                </Text>
                                <View style={styles.cardInfo}>
                                    <Text style={styles.deviceName}>
                                        {device.brand} {device.model}
                                    </Text>
                                    <Text style={styles.deviceMeta}>
                                        {device.category.charAt(0).toUpperCase() + device.category.slice(1)}
                                        {device.condition ? ` · ${device.condition}` : ''}
                                    </Text>
                                    <Text style={[styles.statusBadge, device.status === 'active' ? styles.badgeActive : styles.badgeOther]}>
                                        {device.status ?? 'unknown'}
                                    </Text>
                                </View>
                            </View>
                            <View style={styles.cardActions}>
                                <TouchableOpacity
                                    style={styles.actionBtn}
                                    onPress={() => navigation.navigate('EditDevice', { deviceId: device.id })}
                                >
                                    <Text style={styles.actionEdit}>Edit</Text>
                                </TouchableOpacity>
                                <TouchableOpacity
                                    style={styles.actionBtn}
                                    onPress={() => handleDelete(device)}
                                >
                                    <Text style={styles.actionDelete}>Delete</Text>
                                </TouchableOpacity>
                            </View>
                        </Card>
                    ))
                )}

                <Button
                    title="Add New Device"
                    onPress={() => navigation.navigate('AddDevice')}
                />
                <Button
                    title="Back to Dashboard"
                    variant="outline"
                    onPress={() => navigation.goBack()}
                />
            </ScrollView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    content: { padding: theme.spacing.m },
    card: { marginBottom: theme.spacing.s },
    cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: theme.spacing.s },
    icon: { fontSize: 36, marginRight: theme.spacing.m },
    cardInfo: { flex: 1 },
    deviceName: { ...theme.typography.h2, color: theme.colors.text, fontSize: 18 },
    deviceMeta: { ...theme.typography.caption, color: theme.colors.textSecondary, marginTop: 2 },
    statusBadge: {
        alignSelf: 'flex-start',
        marginTop: theme.spacing.xs,
        paddingHorizontal: theme.spacing.s,
        paddingVertical: 2,
        borderRadius: theme.borderRadius.s,
        fontSize: 11,
        fontWeight: '600',
        overflow: 'hidden',
    },
    badgeActive: { backgroundColor: '#d1fae5', color: '#065f46' },
    badgeOther: { backgroundColor: '#fee2e2', color: '#991b1b' },
    cardActions: { flexDirection: 'row', justifyContent: 'flex-end', gap: theme.spacing.m },
    actionBtn: { padding: theme.spacing.xs },
    actionEdit: { color: theme.colors.primary, fontWeight: '600' },
    actionDelete: { color: theme.colors.error, fontWeight: '600' },
});
