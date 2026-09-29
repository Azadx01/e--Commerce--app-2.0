import React, { useState } from 'react';
import { View, StyleSheet, SafeAreaView, ScrollView, Alert } from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { HomeStackParamList } from '../navigation/types';
import { Header, Button, Input, ErrorMessage, Loading } from '../components';
import { theme } from '../theme/theme';
import { deviceService, DeviceCreate } from '../services/deviceService';
import { ApiError } from '../services/apiClient';

type Props = {
    navigation: NativeStackNavigationProp<HomeStackParamList, 'AddDevice'>;
};

type Category = 'smartphone' | 'laptop';

export const AddDevice = ({ navigation }: Props) => {
    const [category, setCategory] = useState<Category>('smartphone');
    const [brand, setBrand] = useState('');
    const [model, setModel] = useState('');
    const [condition, setCondition] = useState('');
    const [serialNumber, setSerialNumber] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSave = async () => {
        setError('');

        if (!brand.trim() || !model.trim()) {
            setError('Brand and model are required.');
            return;
        }

        setLoading(true);
        try {
            const payload: DeviceCreate = {
                category,
                brand: brand.trim(),
                model: model.trim(),
                condition: condition.trim() || undefined,
                serial_number: serialNumber.trim() || undefined,
            };
            await deviceService.create(payload);
            Alert.alert('Success', 'Device added successfully.', [
                { text: 'OK', onPress: () => navigation.goBack() },
            ]);
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.detail);
            } else {
                setError('Failed to save device. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <Loading />;

    return (
        <SafeAreaView style={styles.container}>
            <Header title="Register Device" />
            <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
                {error ? <ErrorMessage message={error} /> : null}

                {/* Category toggle */}
                <View style={styles.categoryRow}>
                    {(['smartphone', 'laptop'] as Category[]).map((cat) => (
                        <View
                            key={cat}
                            style={[styles.categoryBtn, category === cat && styles.categoryBtnActive]}
                        >
                            <Button
                                title={cat.charAt(0).toUpperCase() + cat.slice(1)}
                                variant={category === cat ? 'primary' : 'outline'}
                                onPress={() => setCategory(cat)}
                            />
                        </View>
                    ))}
                </View>

                <Input
                    label="Brand"
                    value={brand}
                    onChangeText={setBrand}
                    placeholder="e.g. Apple"
                />
                <Input
                    label="Model"
                    value={model}
                    onChangeText={setModel}
                    placeholder="e.g. iPhone 13"
                />
                <Input
                    label="Condition (optional)"
                    value={condition}
                    onChangeText={setCondition}
                    placeholder="e.g. Screen cracked"
                />
                <Input
                    label="Serial / IMEI (optional)"
                    value={serialNumber}
                    onChangeText={setSerialNumber}
                    placeholder="Stored securely — never shown again"
                />

                <View style={styles.spacer} />
                <Button title="Save Device" onPress={handleSave} loading={loading} />
                <Button title="Cancel" variant="outline" onPress={() => navigation.goBack()} />
            </ScrollView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    content: { padding: theme.spacing.m },
    categoryRow: { flexDirection: 'row', gap: theme.spacing.s, marginBottom: theme.spacing.s },
    categoryBtn: { flex: 1 },
    categoryBtnActive: {},
    spacer: { height: theme.spacing.m },
});
